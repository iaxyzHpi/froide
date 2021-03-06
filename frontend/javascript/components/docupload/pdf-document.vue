<template>
  <div class="document mb-3">
    <div class="card">
      <div class="card-header">
        <pdf-header :config="config" :document="document"></pdf-header>
      </div>
      <div class="card-body" :class="{'is-new': document.new}">
        <div v-if="document.uploading" class="progress">
          <div class="progress-bar"
            :class="{'progress-bar-animated progress-bar-striped': progressUnknown}"
            :style="{'width': progressPercentLabel}"
            role="progressbar" :aria-valuenow="document.progress"
            aria-valuemin="0" aria-valuemax="100"></div>
        </div>
        <template v-if="!document.pending">
          <div class="row">
            <div class="col-auto">
              <a :href="document.site_url" target="_blank" class="btn btn-sm btn-light">
                {{ i18n.openAttachmentPage }}
              </a>
              <button class="btn btn-sm btn-light" @click="$emit('loadpdf')">
                {{ i18n.loadPreview }}
              </button>
            </div>
            <div class="ml-auto col-auto">
              <pdf-review :config="config" :document="document"
                @documentupdated="$emit('docupdated', $event)"
              ></pdf-review>
            </div>
          </div>
        </template>
        <div v-else>
          <div class="spinner-border spinner-border-sm" role="status">
            <span class="sr-only">{{ i18n.loading }}</span>
          </div>
          <p>
            {{ i18n.documentPending }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import I18nMixin from '../../lib/i18n-mixin'

import PdfReview from './pdf-review.vue'
import PdfHeader from './pdf-header.vue'

const range = (len) => [...Array(len).keys()]

export default {
  name: 'pdf-document',
  mixins: [I18nMixin],
  props: ['config', 'document'],
  components: {
    PdfReview, PdfHeader
  },
  data () {
    return {
        progressTotal: null,
        progressCurrent: null,
        ready: false,
        pdf: null,
        numPages: null,
        pdfPages: []
    }
  },
  mounted () {
    if (this.document.new) {
      window.setTimeout(() => this.$emit('notnew'), 2000);
    }
    if (this.document.pending) {
      this.checkProgress()
    }
  },
  computed: {
    pages () {
      return this.document.pages
    },
    progressUnknown () {
      return this.progressPercent === null
    },
    progressPercent () {
      if (!this.document.progressTotal) {
        return null
      }
      return this.document.progress / this.document.progressTotal * 100
    },
    progressPercentLabel () {
      if (this.progressPercent) {
        return `${this.progressPercent}%`
      }
      return '100%'
    }
  },
  methods: {
    checkProgress () {
      window.fetch(`/api/v1/attachment/${this.document.id}/`)
        .then(response => response.json()).then((data) => {
          if (data.pending === true) {
            window.setTimeout(() => this.checkProgress(), 5000);
            return
          } else if (data.pending === false) {
            this.$emit('docupdated', {
              pending: false,
              new: true,
              component: 'fullpdf-document',
              site_url: data.site_url,
              file_url: data.file_url,
            })
          } else {
            document.location.reload()
          }
        }).catch(() => {
          window.setTimeout(() => this.checkProgress(), 5000);
        })
    }
  }
}
</script>

<style lang="scss" scoped>
  .document {
    margin-top: 2rem;
  }
  .pages {
    padding-left: 0;
    list-style-type: none;
    white-space: nowrap;
    overflow-x: scroll;
    overflow-scrolling: touch;
  }
  .page {
    display: inline-block;
    max-width: 90px;
    height: 120px;
    margin: 0 1rem;
  }
  .page-image {
    padding: 0 0.25rem;
    width: 100%;
    border: 1px solid #bbb;
  }
</style>
