<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useReportStore } from '../stores/useReportStore';
import { Icon } from '@iconify/vue';
import DocPreview from '../components/editor/DocPreview.vue';
import { renderMarkdown } from '../utils/markdown';
import { asBlob } from 'html-docx-js-typescript';
import { saveAs } from 'file-saver';
import { parseFile } from '../utils/fileParser';

const route = useRoute();
const router = useRouter();
const store = useReportStore();

const currentId = ref(route.params.id);
const title = ref('');
const content = ref('');
const reportSources = ref([]);
const isSaving = ref(false);
const isExporting = ref(false);
const currentFont = ref('"SimSun", "Songti SC", serif');
const isDraft = computed(() => String(currentId.value).startsWith('draft_'));

const messages = ref([]);
const inputValue = ref('');
const chatContainer = ref(null);
const isThinking = ref(false);
const fileInputRef = ref(null);
const uploadedFiles = ref([]);

// 文件预览
const showPreviewModal = ref(false);
const previewContent = ref('');
const previewTitle = ref('');
const isPreviewLoading = ref(false);

const openFilePreview = async (item) => {
  if (!item.file) return;
  previewTitle.value = item.name;
  previewContent.value = '';
  showPreviewModal.value = true;
  isPreviewLoading.value = true;
  try {
    const result = await parseFile(item.file);
    previewContent.value = result.content || '<p>无法解析内容</p>';
  } catch (e) {
    console.error(e);
    previewContent.value = `<p class="text-red-500">无法预览: ${e.message}</p>`;
  } finally {
    isPreviewLoading.value = false;
  }
};

// 加载报告数据（含草稿）
const loadData = () => {
  const id = currentId.value;
  if (String(id).startsWith('draft_') && store.draftReport && store.draftReport.id === id) {
    const draft = store.draftReport;
    title.value = draft.title || '新报告';
    content.value = draft.content || '# 新报告\n\n请开始编辑...';
    reportSources.value = draft.sources || [];
  } else {
    const item = store.reports.find(r => r.id === id);
    if (item) {
      title.value = item.title;
      content.value = item.content;
      reportSources.value = item.sources || [];
    }
  }
  if (messages.value.length === 0) {
    messages.value = [{
      role: 'ai',
      content: '您好！我是您的智能写作助手。我可以帮您修改、扩写或优化报告内容。请告诉我您想要如何调整这份报告。'
    }];
  }
};

onMounted(loadData);

watch(
  () => route.params.id,
  (newId) => {
    if (!newId) return;
    currentId.value = newId;
    loadData();
  }
);

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

// 文件上传
const handleFileSelect = (e) => {
  const files = Array.from(e.target.files || []);
  files.forEach(file => {
    uploadedFiles.value.push({
      id: Date.now() + Math.random(),
      name: file.name,
      size: (file.size / 1024).toFixed(1) + ' KB',
      type: (file.name.split('.').pop() || '').toUpperCase(),
      file
    });
  });
  e.target.value = '';
};

const removeUploadedFile = (id) => {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== id);
};

const triggerFileInput = () => {
  fileInputRef.value?.click();
};

// 发送消息（只显示一次“思考”状态）
const handleSend = async () => {
  const text = inputValue.value.trim();
  const hasFiles = uploadedFiles.value.length > 0;
  if (!text && !hasFiles) return;

  // 添加用户消息（含附件说明）
  const userContent = text || (hasFiles ? `[上传了 ${uploadedFiles.value.length} 个文件]` : '');
  messages.value.push({
    role: 'user',
    content: userContent,
    files: uploadedFiles.value.length ? [...uploadedFiles.value] : undefined
  });

  inputValue.value = '';
  uploadedFiles.value = [];
  scrollToBottom();

  // 仅用 isThinking 控制“思考”显示，不往 messages 里塞思考气泡
  isThinking.value = true;
  scrollToBottom();

  setTimeout(() => {
    isThinking.value = false;

    let updatedContent = content.value;
    let aiResponse = '';

    if (text.includes('修改') || text.includes('更改')) {
      updatedContent = content.value + '\n\n## [AI 补充内容]\n根据您的要求，已对报告进行了相应调整。';
      aiResponse = '已根据您的要求对报告内容进行了修改。您可以在右侧预览中查看更新后的内容。';
    } else if (text.includes('扩写') || text.includes('详细')) {
      updatedContent = content.value + '\n\n### 详细说明\n此处为AI根据您的要求补充的详细内容...';
      aiResponse = '已为您扩写了相关内容。您可以在右侧预览中查看并进一步编辑。';
    } else if (hasFiles && !text) {
      aiResponse = '已收到您上传的文件，如需根据文件内容修改报告，请说明具体需求。';
    } else {
      aiResponse = '我理解您的需求。您可以在右侧预览中直接编辑报告内容，或者告诉我具体需要修改的部分，我会帮您调整。';
    }

    content.value = updatedContent;
    messages.value.push({ role: 'ai', content: aiResponse });
    scrollToBottom();
  }, 2000);
};

// 保存报告（草稿首次保存则入库并跳转）
const handleSave = () => {
  isSaving.value = true;
  setTimeout(() => {
    if (isDraft.value) {
      const newReport = {
        id: 'rpt_' + Date.now(),
        title: title.value,
        create_time: new Date().toLocaleDateString(),
        content: content.value,
        sources: reportSources.value,
        mode: store.draftReport?.mode || 'open'
      };
      store.addReport(newReport);
      store.clearDraftReport();
      router.replace(`/editor/${newReport.id}`);
      currentId.value = newReport.id;
    } else {
      store.updateReport(currentId.value, {
        title: title.value,
        content: content.value
      });
    }
    isSaving.value = false;
  }, 500);
};

// 导出Word
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
      p { margin-bottom: 10pt; text-align: justify; text-indent: 2em; }
      table { border-collapse: collapse; width: 100%; margin: 12pt 0; }
      td, th { border: 1px solid #000; padding: 6pt; text-align: center; }
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

// 返回（草稿未保存则清除草稿）
const goBack = () => {
  if (isDraft.value) {
    store.clearDraftReport();
  }
  router.push('/platform');
};

</script>

<template>
  <div class="flex h-full w-full bg-white overflow-hidden">
    <!-- 左侧：对话区域 -->
    <div class="w-1/2 flex flex-col border-r border-gray-200 bg-gray-50">
      <!-- 顶部工具栏 -->
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

      <!-- 对话内容区 -->
      <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-4 hide-scrollbar">
        <div 
          v-for="(msg, index) in messages" 
          :key="index"
          class="flex flex-col gap-2"
          :class="msg.role === 'user' ? 'items-end' : 'items-start'"
        >
          <div v-if="msg.role === 'ai'" class="flex items-start gap-3 max-w-[85%]">
            <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white shrink-0">
              <Icon icon="ri:robot-2-line" class="text-lg" />
            </div>
            <div class="bg-white p-4 rounded-2xl rounded-tl-none shadow-sm border border-gray-100">
              <p class="text-sm leading-relaxed text-gray-700 whitespace-pre-wrap">{{ msg.content }}</p>
            </div>
          </div>

          <div v-else class="flex flex-col items-end gap-2 max-w-[85%]">
            <div v-if="msg.files && msg.files.length" class="flex flex-wrap justify-end gap-2 mb-1">
              <div
                v-for="f in msg.files"
                :key="f.id"
                class="px-3 py-2 rounded-xl bg-blue-50 border border-blue-100 text-xs text-blue-800 flex items-center gap-2"
              >
                <Icon icon="ri:file-text-line" />
                <span class="truncate max-w-[160px]">{{ f.name }}</span>
              </div>
            </div>
            <div class="bg-blue-600 text-white p-4 rounded-2xl rounded-tr-none shadow-sm">
              <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ msg.content }}</p>
            </div>
          </div>
        </div>

        <!-- 思考中指示器 -->
        <div v-if="isThinking" class="flex items-start gap-3">
          <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white shrink-0">
            <Icon icon="ri:robot-2-line" class="text-lg animate-pulse" />
          </div>
          <div class="bg-white p-4 rounded-2xl rounded-tl-none shadow-sm border border-gray-100 flex items-center">
            <span class="text-sm text-gray-500 mr-2">正在思考...</span>
            <div class="flex gap-1">
              <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入框 + 上传 -->
      <div class="p-4 border-t border-gray-200 shrink-0 bg-white">
        <div v-if="uploadedFiles.length" class="flex flex-wrap gap-2 mb-2">
          <div
            v-for="f in uploadedFiles"
            :key="f.id"
            class="inline-flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-blue-50 border border-blue-100 text-xs text-blue-800"
          >
            <button
              v-if="f.file"
              type="button"
              @click="openFilePreview(f)"
              class="flex items-center gap-2 flex-1 min-w-0 text-left hover:underline"
            >
              <Icon icon="ri:file-text-line" />
              <span class="max-w-[140px] truncate">{{ f.name }}</span>
            </button>
            <template v-else>
              <Icon icon="ri:file-text-line" />
              <span class="max-w-[140px] truncate">{{ f.name }}</span>
            </template>
            <button type="button" @click.stop="removeUploadedFile(f.id)" class="text-blue-400 hover:text-red-500 p-0.5 shrink-0">
              <Icon icon="ri:close-line" />
            </button>
          </div>
        </div>
        <div class="flex items-end gap-2">
          <button
            type="button"
            @click="triggerFileInput"
            class="shrink-0 w-10 h-10 flex items-center justify-center rounded-xl border border-gray-200 text-gray-500 hover:bg-gray-50 hover:border-blue-300 hover:text-blue-600 transition-colors"
            title="上传文件"
          >
            <Icon icon="ri:attachment-2" class="text-lg" />
          </button>
          <input ref="fileInputRef" type="file" class="hidden" multiple accept=".pdf,.doc,.docx,.txt" @change="handleFileSelect" />
          <div class="flex-1 bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
            <textarea 
              v-model="inputValue"
              @keydown.enter.exact.prevent="handleSend"
              rows="1"
              class="w-full p-3 bg-transparent outline-none resize-none text-sm text-gray-700 placeholder-gray-400 max-h-32 overflow-y-auto hide-scrollbar"
              placeholder="输入修改建议或上传文件..."
            ></textarea>
          </div>
          <button 
            @click="handleSend"
            :disabled="!inputValue.trim() && uploadedFiles.length === 0"
            class="w-10 h-10 flex items-center justify-center rounded-xl bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            <Icon icon="ri:send-plane-fill" class="text-lg" />
          </button>
        </div>
      </div>
    </div>

    <!-- 右侧：报告预览（可编辑） -->
    <div class="w-1/2 bg-gray-100 flex flex-col relative">
      <!-- 预览工具栏 -->
      <div class="h-12 px-6 border-b border-gray-200/50 flex items-center justify-between shrink-0 bg-gray-50/80 backdrop-blur z-10">
        <span class="text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center gap-2">
          <Icon icon="ri:file-search-line" /> 报告预览
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
      
      <!-- 预览/编辑内容区 -->
      <div class="flex-1 overflow-hidden relative flex flex-col">
        <!-- 预览区域（可滚动） -->
        <div class="flex-1 overflow-y-auto bg-gray-100/50">
          <DocPreview 
            :content="content" 
            :font-family="currentFont" 
            :sources="reportSources"
          />
        </div>
        
        <!-- 底部编辑区域（固定在底部） -->
        <div class="shrink-0 border-t border-gray-300 bg-white shadow-lg">
          <div class="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50">
            <span class="text-xs font-semibold text-gray-600 flex items-center gap-2">
              <Icon icon="ri:edit-line" />
              直接编辑报告内容
            </span>
            <span class="text-xs text-gray-400">支持 Markdown 格式</span>
          </div>
          <div class="p-4">
            <textarea
              v-model="content"
              rows="4"
              class="w-full p-3 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm text-gray-700 font-mono resize-none"
              placeholder="在此直接编辑报告内容...（支持 Markdown 格式）"
            ></textarea>
            <div class="mt-2 flex items-center justify-between">
              <span class="text-xs text-gray-400">{{ isDraft ? '未保存到库，点击下方保存后入库' : '修改后请点击保存' }}</span>
              <button
                @click="handleSave"
                class="px-4 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-medium hover:bg-blue-700 transition-colors flex items-center gap-1.5"
              >
                <Icon icon="ri:save-3-line" />
                手动保存
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文件预览弹窗 -->
    <div v-if="showPreviewModal" class="fixed inset-0 z-[200] bg-black/50 flex items-center justify-center p-4" @click.self="showPreviewModal = false">
      <div class="bg-white w-full max-w-3xl max-h-[85vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-200 flex justify-between items-center shrink-0">
          <h3 class="text-lg font-bold text-gray-800 truncate pr-4">{{ previewTitle }}</h3>
          <button type="button" @click="showPreviewModal = false" class="p-2 rounded-lg hover:bg-gray-100 text-gray-600">
            <Icon icon="ri:close-line" class="text-xl" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6 min-h-0">
          <div v-if="isPreviewLoading" class="flex items-center justify-center py-12 text-gray-500">
            <Icon icon="ri:loader-4-line" class="animate-spin text-3xl" />
          </div>
          <div v-else class="prose prose-sm max-w-none" v-html="previewContent"></div>
        </div>
      </div>
    </div>
  </div>
</template>
