<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- 顶部工具栏 -->
    <div class="shrink-0 px-10 pt-10 pb-4 flex justify-between items-center">
      <div class="flex items-center gap-3">
        <h1 class="text-2xl font-bold text-gray-800">我的报告</h1>
        <span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold">
          {{ store.reports.length }}
        </span>
      </div>
      
      <button 
        @click="$router.push('/new-report')"
        class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-blue-200 transition-all hover:-translate-y-0.5"
      >
        <Icon icon="ri:sparkling-2-fill" class="text-lg" />
        新建报告
      </button>
    </div>

    <!-- 可滚动内容区：报告卡片列表 -->
    <div class="flex-1 overflow-y-auto px-10 pb-10">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="report in store.reports" 
          :key="report.id"
          class="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 hover:shadow-md transition-all group"
        >
          <div class="flex justify-between items-start mb-4">
            <div class="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
              <Icon icon="material-symbols:article-outline" class="text-2xl" />
            </div>
            <div class="flex gap-2">
               <button 
                @click="$router.push(`/editor/${report.id}`)"
                class="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-blue-600 transition-colors"
                title="编辑"
              >
                <Icon icon="material-symbols:edit-outline" class="text-lg" />
              </button>
              <button 
                @click.stop="confirmDelete(report.id)"
                class="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-red-500 transition-colors"
                title="删除"
              >
                <Icon icon="material-symbols:delete-outline" class="text-lg" />
              </button>
            </div>
          </div>

          <h3 class="font-bold text-lg text-slate-800 mb-2 line-clamp-2 min-h-[3.5rem]">
            {{ report.title }}
          </h3>

          <div class="flex items-center gap-2 text-xs text-slate-400 mb-4">
            <Icon icon="material-symbols:calendar-today-outline" />
            <span>{{ report.create_time }}</span>
          </div>

          <p class="text-slate-500 text-sm mb-6 line-clamp-3 bg-slate-50 p-3 rounded-lg h-24">
            {{ report.content.substring(0, 100) }}...
          </p>

          <button 
            @click="openPreview(report)"
            class="w-full py-2.5 rounded-xl border border-slate-200 text-slate-600 font-medium text-sm hover:border-blue-600 hover:text-blue-600 hover:bg-blue-50 transition-all flex items-center justify-center gap-2"
          >
            <span>预览报告</span>
            <Icon icon="material-symbols:visibility-outline" />
          </button>
        </div>
      </div>
    </div>

  <!-- Report Preview Modal -->
  <div v-if="showPreviewModal && selectedReport" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white w-full max-w-4xl h-[85vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-modal">
          <div class="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50 shrink-0">
              <div>
                  <h3 class="text-lg font-bold text-gray-900">{{ selectedReport.title }}</h3>
                  <p class="text-sm text-gray-500">预览模式</p>
              </div>
              <div class="flex gap-3">
                  <button class="px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg transition-colors" @click="closePreview">
                      取消
                  </button>
                  <button class="px-5 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 shadow-md transition-colors" @click="continueEdit">
                      <Icon icon="ri:edit-box-line" class="inline text-lg mr-1"/> 继续编辑
                  </button>
              </div>
          </div>
          <DocPreview :content="selectedReport.content" class="flex-1 min-h-0 bg-gray-50" />
      </div>
  </div>


  <!-- Delete Confirmation Modal -->
  <ConfirmModal 
    :show="showDeleteModal"
    title="删除报告"
    content="确定要删除这个报告吗？删除后将无法恢复。"
    @close="showDeleteModal = false"
    @confirm="handleDeleteConfirm"
  />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
// 别忘了引入 Icon
import { Icon } from '@iconify/vue';
import { useReportStore } from '../stores/useReportStore';
import DocPreview from '../components/editor/DocPreview.vue';
import ConfirmModal from '../components/common/ConfirmModal.vue';

const store = useReportStore();
const router = useRouter();

const showPreviewModal = ref(false);
const selectedReport = ref(null);

const openPreview = (report) => {
    selectedReport.value = report;
    showPreviewModal.value = true;
};

const closePreview = () => {
    showPreviewModal.value = false;
    selectedReport.value = null;
};

const continueEdit = () => {
    const rpt = selectedReport.value;
    closePreview();
    router.push(`/editor/${rpt.id}`);
};

// Delete Confirmation Logic
const showDeleteModal = ref(false);
const itemToDelete = ref(null);

const confirmDelete = (id) => {
    itemToDelete.value = id;
    showDeleteModal.value = true;
};

const handleDeleteConfirm = () => {
    if (itemToDelete.value) {
        store.deleteReport(itemToDelete.value);
        showDeleteModal.value = false;
        itemToDelete.value = null;
    }
};
</script>