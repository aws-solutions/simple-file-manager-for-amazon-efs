import { mount } from '@vue/test-utils'
import { BModal } from 'bootstrap-vue'
import Filesystem from '@/routes/Filesystem.vue'

const $route = {
    params: {id: '1234'}
}


describe("Filesystem.vue", () => {
    it("simple  mount", async () => {
      const wrapper = mount(Filesystem, {
        mocks: {
            $route
        },
        stubs: {
            'b-modal': BModal
        }
      });
      console.log(wrapper.vm);
    });
  });