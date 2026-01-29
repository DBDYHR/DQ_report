<script setup>
import { ref, computed, nextTick, watch, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { Icon } from '@iconify/vue';
import { useReportStore } from '../stores/useReportStore';
import { parseFile } from '../utils/fileParser';

const router = useRouter();
const store = useReportStore();

const reportMode = ref('open');
const selectedTemplateId = ref(null);
const localFiles = ref([]); // { id, name, file } 便于预览
const inputPrompt = ref('');
const isGenerating = ref(false);
const loadingText = ref('准备开始...');
const fileInputRef = ref(null);
const showTemplatePanel = ref(false);
const templatePanelRef = ref(null);
const templateButtonRef = ref(null);

const categories = computed(() => store.templates);

const selectedTemplateName = computed(() => {
  if (!selectedTemplateId.value) return null;
  for (const cat of store.templates) {
    const t = cat.list.find(i => i.id === selectedTemplateId.value);
    if (t) return t.title;
  }
  return null;
});

const selectTemplate = (id) => {
  selectedTemplateId.value = id;
  showTemplatePanel.value = false;
};

const handleFileChange = (e) => {
  const files = Array.from(e.target.files || []);
  files.forEach(file => {
    localFiles.value.push({
      id: Date.now() + Math.random(),
      name: file.name,
      file
    });
  });
  e.target.value = '';
};

const removeFile = (idx) => {
  localFiles.value.splice(idx, 1);
};

const triggerFileInput = () => {
  fileInputRef.value?.click();
};

// 点击外部关闭模板面板（延迟绑定，避免打开时立刻被关）
const onDocumentClick = (e) => {
  if (!templatePanelRef.value || !templateButtonRef.value) return;
  if (templatePanelRef.value.contains(e.target) || templateButtonRef.value.contains(e.target)) return;
  showTemplatePanel.value = false;
};

const toggleTemplatePanel = () => {
  showTemplatePanel.value = !showTemplatePanel.value;
  if (showTemplatePanel.value) {
    nextTick(() => {
      setTimeout(() => document.addEventListener('click', onDocumentClick), 10);
    });
  } else {
    document.removeEventListener('click', onDocumentClick);
  }
};

watch(showTemplatePanel, (v) => {
  if (!v) document.removeEventListener('click', onDocumentClick);
});
onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick);
});

const canStart = computed(() => {
  if (reportMode.value === 'professional') {
    return selectedTemplateId.value && localFiles.value.length > 0;
  }
  return true;
});

// 专业报告：生成后存草稿并跳转
const runProfessionalGeneration = () => {
  isGenerating.value = true;
  const steps = [
    `正在解析 ${localFiles.value[0].name} 等 ${localFiles.value.length} 份文件...`,
    "正在分析语义结构与关键数据...",
    "正在构建图表与结论章节...",
    "即将完成..."
  ];
  let stepIndex = 0;
  loadingText.value = steps[0];
  const interval = setInterval(() => {
    stepIndex++;
    if (stepIndex < steps.length) loadingText.value = steps[stepIndex];
  }, 2000);

  setTimeout(() => {
    clearInterval(interval);
    let tplName = "未命名模板";
    store.templates.forEach(cat => {
      const t = cat.list.find(i => i.id === selectedTemplateId.value);
      if (t) tplName = t.title;
    });
    const demoContent = store.reports[0]?.content || '# 新报告\n\n请开始编辑...';
    const draftId = 'draft_' + Date.now();
    store.setDraftReport({
      id: draftId,
      title: inputPrompt.value.trim() || `基于 ${tplName} 的智能分析报告`,
      create_time: new Date().toLocaleDateString(),
      content: demoContent,
      sources: localFiles.value.map(f => f.name),
      mode: 'professional',
      templateId: selectedTemplateId.value
    });
    router.push(`/editor/${draftId}`);
  }, 8000);
};

// 开放报告：存草稿并跳转（不入库）
const startOpenReport = () => {
  const draftId = 'draft_' + Date.now();
  let initialContent = '# 新报告\n\n请开始编辑或通过左侧对话继续创作...';
  if (selectedTemplateId.value) {
    for (const cat of store.templates) {
      const t = cat.list.find(i => i.id === selectedTemplateId.value);
      if (t) {
        initialContent = t.content;
        break;
      }
    }
  }
  store.setDraftReport({
    id: draftId,
    title: inputPrompt.value.trim() || '新报告',
    create_time: new Date().toLocaleDateString(),
    content: initialContent,
    sources: localFiles.value.map(f => f.name),
    mode: 'open',
    templateId: selectedTemplateId.value || null
  });
  router.push(`/editor/${draftId}`);
};

const handleStart = () => {
  if (reportMode.value === 'professional') {
    if (!selectedTemplateId.value || localFiles.value.length === 0) return;
    runProfessionalGeneration();
  } else {
    startOpenReport();
  }
};

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
</script>

<template>
  <div class="flex flex-col h-full bg-[#f0f2f5]">
    <!-- 居中：Logo + 对话框 -->
    <div class="flex-1 flex flex-col items-center justify-center px-4 py-8 min-h-0">
      <!-- Logo -->
      <div class="mb-6 flex flex-col items-center">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] flex items-center justify-center text-white shadow-lg">
          <Icon icon="ri:edit-document-line" class="text-4xl" />
        </div>
        <p class="mt-3 text-sm font-medium text-[#6b7280]">帮我写作</p>
      </div>

      <!-- 对话框卡片 -->
      <div class="w-full max-w-2xl rounded-2xl bg-white shadow-xl border border-[#e5e7eb] overflow-hidden">
        <!-- 欢迎语 -->
        <div class="px-6 pt-6 pb-4 border-b border-[#f3f4f6]">
          <p class="text-[15px] leading-relaxed text-[#374151]">
            选择 <strong>专业报告</strong>（按模板+材料生成）或 <strong>开放报告</strong>（自由创作，可选模板）。在下方选择模式、模板并上传资料后开始。
          </p>
        </div>

        <!-- 工具栏 -->
        <div class="px-6 pt-4 pb-4 space-y-4">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-medium text-[#6b7280] w-12">模式</span>
            <div class="flex rounded-lg overflow-hidden border border-[#e5e7eb] bg-[#f9fafb]">
              <button
                type="button"
                @click="reportMode = 'open'"
                :class="['px-4 py-2 text-sm font-medium transition-colors', reportMode === 'open' ? 'bg-[#6366f1] text-white' : 'text-[#6b7280] hover:bg-white']"
              >
                开放报告
              </button>
              <button
                type="button"
                @click="reportMode = 'professional'"
                :class="['px-4 py-2 text-sm font-medium transition-colors', reportMode === 'professional' ? 'bg-[#6366f1] text-white' : 'text-[#6b7280] hover:bg-white']"
              >
                专业报告
              </button>
            </div>
          </div>

          <!-- 模板：两种模式都显示 -->
          <div class="flex flex-wrap items-center gap-2" ref="templateButtonRef">
            <span class="text-xs font-medium text-[#6b7280] w-12">模板</span>
            <div class="relative">
              <button
                type="button"
                @click="toggleTemplatePanel"
                class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-[#e5e7eb] bg-white text-sm font-medium text-[#374151] hover:bg-[#f9fafb] hover:border-[#6366f1]/50"
              >
                <Icon icon="ri:file-list-2-line" class="text-[#6366f1]" />
                {{ selectedTemplateName || '选择模板（可选）' }}
                <Icon icon="ri:arrow-down-s-line" class="text-[#9ca3af]" />
              </button>
              <!-- 下拉在按钮下方，避免被裁掉 -->
              <div
                v-if="showTemplatePanel"
                ref="templatePanelRef"
                class="absolute left-0 top-full mt-2 w-[340px] max-h-[300px] overflow-y-auto rounded-xl border border-[#e5e7eb] bg-white shadow-lg z-[100] py-2"
              >
                <div v-for="cat in categories" :key="cat.name" class="px-3 py-1">
                  <p class="text-[11px] font-semibold text-[#9ca3af] uppercase tracking-wider mb-1.5 px-1">{{ cat.name }}</p>
                  <button
                    v-for="tpl in cat.list"
                    :key="tpl.id"
                    type="button"
                    @click="selectTemplate(tpl.id)"
                    :class="['w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors', selectedTemplateId === tpl.id ? 'bg-[#eef2ff] text-[#6366f1] font-medium' : 'text-[#374151] hover:bg-[#f3f4f6]']"
                  >
                    {{ tpl.title }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs font-medium text-[#6b7280] w-12">文件</span>
            <button
              type="button"
              @click="triggerFileInput"
              class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-[#e5e7eb] bg-white text-sm font-medium text-[#374151] hover:bg-[#f9fafb] hover:border-[#6366f1]/50"
            >
              <Icon icon="ri:attachment-2" />
              上传文件
            </button>
            <input ref="fileInputRef" type="file" class="hidden" multiple accept=".pdf,.doc,.docx,.txt" @change="handleFileChange" />
          </div>

          <div v-if="localFiles.length > 0" class="flex flex-wrap gap-2">
            <button
              v-for="(item, idx) in localFiles"
              :key="item.id"
              type="button"
              @click="openFilePreview(item)"
              class="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-[#f0f9ff] border border-[#bae6fd] text-sm text-[#0369a1] hover:bg-[#e0f2fe]"
            >
              <Icon icon="ri:file-text-line" />
              <span class="max-w-[160px] truncate">{{ item.name }}</span>
              <button type="button" @click.stop="removeFile(idx)" class="text-[#0ea5e9] hover:text-[#ef4444] p-0.5">
                <Icon icon="ri:close-line" />
              </button>
            </button>
          </div>

          <!-- 输入框 + 发送 -->
          <div class="flex items-end gap-2 pt-2">
            <textarea
              v-model="inputPrompt"
              rows="2"
              class="flex-1 min-h-[80px] py-3 px-4 rounded-xl border border-[#e5e7eb] outline-none resize-none text-[15px] text-[#1f2937] placeholder-[#9ca3af] focus:ring-2 focus:ring-[#6366f1]/30 focus:border-[#6366f1]/50"
              :placeholder="reportMode === 'professional' ? '简述报告主题或要求（可选）' : '输入报告主题或写作要求...'"
            />
            <button
              type="button"
              @click="handleStart"
              :disabled="!canStart"
              class="shrink-0 w-12 h-12 rounded-xl flex items-center justify-center text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              :class="canStart ? 'bg-[#6366f1] hover:bg-[#4f46e5] shadow-md' : 'bg-[#d1d5db]'"
            >
              <Icon v-if="isGenerating" icon="ri:loader-4-line" class="animate-spin text-2xl" />
              <Icon v-else icon="ri:send-plane-fill" class="text-xl" />
            </button>
          </div>
        </div>
      </div>

      <p class="mt-4 text-center text-xs text-[#9ca3af]">
        {{ reportMode === 'professional' ? '专业报告需选择模板并上传至少一份文件' : '开放报告可直接开始，可选模板与上传文件' }}
      </p>
    </div>

    <!-- 文件预览弹窗 -->
    <div v-if="showPreviewModal" class="fixed inset-0 z-[200] bg-black/50 flex items-center justify-center p-4" @click.self="showPreviewModal = false">
      <div class="bg-white w-full max-w-3xl max-h-[85vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        <div class="px-5 py-4 border-b border-[#e5e7eb] flex justify-between items-center shrink-0">
          <h3 class="text-lg font-bold text-[#1f2937] truncate pr-4">{{ previewTitle }}</h3>
          <button type="button" @click="showPreviewModal = false" class="p-2 rounded-lg hover:bg-[#f3f4f6] text-[#6b7280]">
            <Icon icon="ri:close-line" class="text-xl" />
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6 min-h-0">
          <div v-if="isPreviewLoading" class="flex items-center justify-center py-12 text-[#6b7280]">
            <Icon icon="ri:loader-4-line" class="animate-spin text-3xl" />
          </div>
          <div v-else class="prose prose-sm max-w-none" v-html="previewContent"></div>
        </div>
      </div>
    </div>

    <!-- 生成中遮罩 -->
    <div v-if="isGenerating" class="fixed inset-0 z-50 bg-white/90 backdrop-blur-sm flex flex-col items-center justify-center">
      <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] flex items-center justify-center shadow-xl mb-4">
        <Icon icon="ri:robot-line" class="text-3xl text-white animate-pulse" />
      </div>
      <p class="text-lg font-semibold text-[#1f2937]">正在生成报告...</p>
      <p class="text-sm text-[#6b7280] mt-1 font-mono">{{ loadingText }}</p>
    </div>
  </div>
</template>
