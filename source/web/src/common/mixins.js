// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
export const uploaderMixin = {
  inject: ['uploader']
}

export const supportMixin = {
  data () {
    return {
      support: true
    }
  },
  mounted () {
    this.support = this.uploader.uploader.support
  }
}
