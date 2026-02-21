<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useReportStore } from '../stores/useReportStore';
import { Icon } from '@iconify/vue';
import DocPreview from '../components/editor/DocPreview.vue';
// 1. 确保引入了 AI 组件
import AiAssistant from '../components/editor/AiAssistant.vue';
import { asBlob } from 'html-docx-js-typescript';
import { saveAs } from 'file-saver';
import { renderMarkdown } from '../utils/markdown';

const route = useRoute();
const router = useRouter();
const store = useReportStore();

// 状态
const currentId = ref(route.params.id);
const title = ref('');
const content = ref('');
const isSaving = ref(false);
const isExporting = ref(false);
const currentFont = ref('"SimSun", "Songti SC", serif');
const reportSources = ref([]);

// 根据当前 ID 加载报告 / 模板数据
const loadData = () => {
  // 1. 尝试从 reports 找
  let item = store.reports.find(r => r.id === currentId.value);
  
  // 2. 如果没找到，尝试从模板里找
  if (!item) {
    store.templates.forEach(cat => {
      const found = cat.list.find(t => t.id === currentId.value);
      if (found) item = found;
    });
  }

  if (item) {
    title.value = item.title;
    content.value = item.content;
    reportSources.value = item.sources || [];
  } else {
    // 如果找不到 ID，可能是新建，或者是无效 ID
    // 检查是否有 query mode
    const isTemplate = route.query.mode === 'template';
    title.value = isTemplate ? "新建模板" : "新报告";
    content.value = isTemplate ? "# 模板标题\n" : "# 报告标题\n";
    reportSources.value = [];
  }
};

// 初始化：根据 ID 获取数据
onMounted(loadData);

// 监听路由参数变化（例如从一个模板跳到另一个模板）
watch(
  () => route.params.id,
  (newId) => {
    if (!newId) return;
    currentId.value = newId;
    loadData();
  }
);

// 保存功能
const handleSave = () => {
  isSaving.value = true;
  setTimeout(() => {
    const isTemplate = route.query.mode === 'template';
    
    if (isTemplate) {
      store.updateTemplate(currentId.value, {
        title: title.value,
        content: content.value
      });
    } else {
    // 默认是报告
      store.updateReport(currentId.value, {
        title: title.value,
        content: content.value
      });
    }
    
    // alert('保存成功！');
    isSaving.value = false;
    
    // 保存后自动返回？或者留在这里？
    // 这里选择留在这里提示一下
  }, 500);
};

// 导出功能
const handleExport = async () => {
  if (isExporting.value) return;
  isExporting.value = true;
  
  try {
    const htmlBody = renderMarkdown(content.value);
    const css = `
      body { font-family: "SimSun", "Songti SC", serif; font-size: 12pt; line-height: 1.8; }
      h1 { font-size: 22pt; font-weight: bold; text-align: center; margin: 24pt 0 18pt 0; }
      h2 { font-size: 16pt; font-weight: bold; margin: 18pt 0 12pt 0; border-bottom: 1px solid #000; padding-bottom: 4pt; }
      h3 { font-size: 14pt; font-weight: bold; margin: 12pt 0 6pt 0; }
      p { margin-bottom: 10pt; text-align: left; }
      table { border-collapse: collapse; width: 100%; margin: 12pt 0; }
      td, th { border: 1px solid #000; padding: 6pt; text-align: center; }
      blockquote { border-left: 4px solid #ccc; padding-left: 10pt; margin: 10pt 0; color: #666; }
    `;
    
    const fullHtml = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <style>${css}</style>
        </head>
        <body>${htmlBody}</body>
      </html>
    `;
    
    const blob = await asBlob(fullHtml, {
      orientation: 'portrait',
      margins: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
    });
    
    saveAs(blob, `${title.value || '未命名报告'}.docx`);
  } catch (error) {
    console.error('Export error:', error);
    alert('导出失败，请重试');
  } finally {
    isExporting.value = false;
  }
};

// 返回上一页
const goBack = () => {
  const isTemplate = route.query.mode === 'template';
  if (isTemplate) {
    router.push('/templates');
  } else {
    // 如果是从平台来的就回平台，如果是 Chat 来的就回 Chat
    // 这里简单处理，默认回平台(我的报告列表)
    // 实际上平台模式目前就是我的报告列表
    router.push('/platform');
  }
};
</script>

<template>
  <div class="flex h-full w-full bg-white overflow-hidden">
    
    <div class="w-1/2 flex flex-col border-r border-gray-200 shadow-[4px_0_24px_rgba(0,0,0,0.02)] z-10">
      
      <div class="h-16 px-6 border-b border-gray-200 flex items-center justify-between shrink-0 bg-white">
        <div class="flex items-center gap-3 flex-1 mr-4">
          <button 
            @click="goBack" 
            class="w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded-lg text-gray-500 transition-colors" 
            title="返回"
          >
            <Icon icon="ri:arrow-left-line" class="text-xl" />
          </button>
          <div class="h-6 w-px bg-gray-200 mx-1"></div>
          <input 
            v-model="title" 
            class="flex-1 text-lg font-bold outline-none placeholder-gray-300 text-gray-800" 
            type="text" 
            placeholder="输入标题..."
          />
        </div>
        
        <div class="flex gap-2">
          <button 
            @click="handleExport"
            :disabled="isExporting"
            class="px-3 py-2 border border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 flex items-center gap-2 text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon v-if="isExporting" icon="ri:loader-4-line" class="animate-spin" />
            <Icon v-else icon="ri:file-word-line" /> 
            {{ isExporting ? '导出中...' : '导出' }}
          </button>
          
          <button 
            @click="handleSave" 
            class="px-5 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 shadow-md flex items-center gap-2 text-sm transition-all disabled:opacity-70"
            :disabled="isSaving"
          >
            <Icon v-if="isSaving" icon="ri:loader-4-line" class="animate-spin" />
            <Icon v-else icon="ri:save-3-line" />
            {{ isSaving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>

      <div class="flex-1 bg-gray-50 p-6 overflow-hidden flex flex-col gap-4 relative">
        <div class="flex-1 flex flex-col min-h-0 bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm focus-within:ring-2 focus-within:ring-blue-100 transition-shadow">
          <textarea 
            v-model="content" 
            class="w-full h-full p-6 outline-none resize-none text-gray-700 font-mono text-sm leading-7 hide-scrollbar" 
            placeholder="# 在此输入 Markdown 内容..."
          ></textarea>
        </div>

        <div class="h-[280px] shrink-0 z-20 pt-2">
          <AiAssistant v-model="content" :title="title" />
        </div>
      </div>
    </div>

    <div class="w-1/2 bg-gray-100 relative flex flex-col">
      <div class="h-12 px-6 border-b border-gray-200/50 flex items-center justify-between shrink-0 bg-gray-50/80 backdrop-blur z-10">
        <span class="text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center gap-2">
          <Icon icon="ri:file-search-line" /> 文档预览 (A4)
        </span>
        
        <div class="flex items-center gap-2">
          <Icon icon="ri:font-size" class="text-gray-400 text-sm" />
          <select 
            v-model="currentFont" 
            class="text-xs border border-gray-200 rounded px-2 py-1 bg-white hover:border-blue-300 focus:outline-none focus:border-blue-500 transition-colors cursor-pointer text-gray-600"
          >
            <option value='"SimSun", "Songti SC", serif'>仿宋 (标准)</option>
            <option value='"SimHei", "Heiti SC", sans-serif'>黑体</option>
            <option value='"KaiTi", "Kaiti SC", serif'>楷体</option>
            <option value='"Microsoft YaHei", sans-serif'>微软雅黑</option>
          </select>
        </div>
      </div>
      
      <DocPreview 
        :content="content" 
        :font-family="currentFont" 
        :sources="reportSources"
      />
    </div>

  </div>
</template>