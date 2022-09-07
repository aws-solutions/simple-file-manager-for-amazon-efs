import {createLocalVue, shallowMount} from '@vue/test-utils'
import makedir from '@/components/makedir.vue'
import {BootstrapVue, BootstrapVueIcons} from "bootstrap-vue";

const localVue = createLocalVue()

localVue.use(BootstrapVue)
localVue.use(BootstrapVueIcons)

const ID = '1234';
const $route = {
  path: '/filesystem/:id',
  hash: '',
  params: {id: ID}
}

describe('makedir.vue', () => {
    it('test mount component', async () => {
        const postDirData = jest.fn().mockReturnValue({'statusCode': 500})

        makedir.methods.postDirData = postDirData
        const wrapper = await shallowMount(makedir, {
        mocks: {
            $route
        },
        localVue
        });
        
        wrapper.vm.$nextTick(() => {
            wrapper.vm.createDirectory()
            expect(wrapper.emitted().dirCreated).toBeTruthy()
        })

  });


});