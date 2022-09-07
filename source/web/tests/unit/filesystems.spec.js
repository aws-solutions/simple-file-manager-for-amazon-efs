import {createLocalVue, shallowMount} from '@vue/test-utils'
import filesystems from '@/components/filesystems.vue'
import {BootstrapVue, BootstrapVueIcons} from "bootstrap-vue";

const localVue = createLocalVue()

localVue.use(BootstrapVue)
localVue.use(BootstrapVueIcons)


describe('filesystems.vue', () => {
    it('test mount component with 0 filesystems', async () => {
        const getFileSystemData = jest.fn().mockReturnValue({'filesystems': []})

        filesystems.methods.getFileSystemData = getFileSystemData
        const wrapper = await shallowMount(filesystems, {
        localVue
        });
    expect(wrapper.vm.filesystems.length).toBe(0);
  });
  
    it('test mount component with 1 filesystems', async () => {
        const getFileSystemData = jest.fn().mockReturnValue({'filesystems': [{"name": "1234"}]})

        filesystems.methods.getFileSystemData = getFileSystemData
    
        const wrapper = await shallowMount(filesystems, {
        localVue
        });
        
        expect(wrapper.vm.filesystems.length).toBe(1);
  });


});