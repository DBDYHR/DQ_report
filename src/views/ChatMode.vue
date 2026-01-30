<script setup>
import { ref, nextTick, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Icon } from '@iconify/vue';
import { useReportStore } from '../stores/useReportStore';
import DocPreview from '../components/editor/DocPreview.vue';
import { parseFile } from '../utils/fileParser';
import { renderMarkdown } from '../utils/markdown';
import openSample from '../assets/open_sample.txt?raw';
import professionalSample from '../assets/professional_sample.txt?raw';

const router = useRouter();
const store = useReportStore();

// 聊天记录
const messages = ref([
  {
    role: 'ai',
    content: '您好！我是您的智能写作助手。我们可以开始撰写您的行业分析报告，或者您想针对某个特定主题进行深度研究？'
  }
]);

const inputValue = ref('');
const chatContainer = ref(null);
const textareaRef = ref(null);
const isThinking = ref(false);
const isGenerating = ref(false);
const generationStep = ref('正在初始化报告环境...');

// File Upload Logic
const fileInput = ref(null);
const uploadedFiles = ref([]);

const triggerFileUpload = () => {
  fileInput.value.click();
};

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files);
  files.forEach(file => {
    uploadedFiles.value.push({
      id: Date.now() + Math.random(),
      name: file.name,
      size: (file.size / 1024).toFixed(1) + ' KB',
      type: file.name.split('.').pop().toUpperCase(),
      file: file // Store raw file for parsing
    });
  });
  event.target.value = '';
};

const removeFile = (id) => {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== id);
};

// Template Selector Logic
const showTemplateSelector = ref(false);
const handleSelectTemplate = (template) => {
    uploadedFiles.value.push({
        id: template.id,
        name: template.title,
        size: 'TEMPLATE',
        type: 'TPL'
    });
    showTemplateSelector.value = false;
};

// File Styling Helper
const getFileStyle = (type) => {
    const t = type ? type.toUpperCase() : 'UNKNOWN';
    if (['DOC', 'DOCX'].includes(t)) {
        return { 
            icon: 'ri:file-word-2-fill', 
            color: 'bg-blue-600', 
            text: 'text-blue-700', // Darker text for title
            badge: 'bg-blue-600',
            bg: 'bg-[#eff4ff]', 
            border: 'border-blue-100' 
        };
    }
    if (t === 'PDF') {
        return { 
            icon: 'ri:file-pdf-fill', 
            color: 'bg-red-500', 
            text: 'text-red-700',
            badge: 'bg-red-500', 
            bg: 'bg-red-50', 
            border: 'border-red-100' 
        };
    }
    if (t === 'TXT') {
        return { 
            icon: 'ri:file-text-fill', 
            color: 'bg-orange-500', 
            text: 'text-orange-700',
            badge: 'bg-orange-500', 
            bg: 'bg-orange-50', 
            border: 'border-orange-100' 
        };
    }
    if (t === 'TPL') {
         return { 
            icon: 'ri:layout-grid-fill', 
            color: 'bg-purple-500', 
            text: 'text-purple-700',
            badge: 'bg-purple-500', 
            bg: 'bg-purple-50', 
            border: 'border-purple-100' 
        };
    }
    return { 
        icon: 'ri:file-fill', 
        color: 'bg-slate-500', 
        text: 'text-slate-700',
        badge: 'bg-slate-500', 
        bg: 'bg-slate-100', 
        border: 'border-slate-200' 
    };
};

// Preview Logic
const showPreviewModal = ref(false);
const previewContent = ref('');
const previewTitle = ref('');

// Report Mode Logic
const reportMode = ref('open'); // 'pro' | 'open'
const showModeSelector = ref(false);

const handleSelectMode = (mode) => {
    reportMode.value = mode;
    showModeSelector.value = false;
};

const openFilePreview = async (file) => {
    previewTitle.value = file.name;

    if (file.type === 'TPL') {
        let content = '';
        // Search in store
        for (const cat of store.templates) {
            const found = cat.list.find(t => t.id === file.id);
            if (found) {
                content = found.content;
                previewTitle.value = found.title;
                break;
            }
        }
        if (content) {
            previewContent.value = content;
            showPreviewModal.value = true;
        }
    } else if (file.file) {
        // Real file parsing
        previewContent.value = '<div class="text-center py-10 text-gray-500">正在解析文件内容...</div>';
        showPreviewModal.value = true;
        
        try {
            const result = await parseFile(file.file);
            previewContent.value = result.content;
        } catch (e) {
            console.error(e);
            previewContent.value = `<div class="p-4 text-red-500">无法预览文件: ${e.message}</div>`;
        }
    } else {
        // Fallback
        previewContent.value = `<div class="p-4">预览暂不可用</div>`;
        showPreviewModal.value = true;
    }
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

// 文本框高度自适应
const autoResize = () => {
  const el = textareaRef.value;
  if (el) {
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  }
};

// 发送消息
const handleSend = () => {
  const text = inputValue.value.trim();
  // Allow sending if text exists OR files exist
  if (!text && uploadedFiles.value.length === 0) return;

  // 1. 下发用户消息
  messages.value.push({ 
    role: 'user', 
    content: text,
    files: [...uploadedFiles.value]
  });
  
  inputValue.value = '';
  uploadedFiles.value = []; // Clear files after send
  
  // 重置高度
  if (textareaRef.value) textareaRef.value.style.height = 'auto';
  scrollToBottom();

  // 2. AI 思考演示 (设置延时)
  isThinking.value = true;
  
  setTimeout(() => {
    isThinking.value = false;
    
    // 3. 给出分析结果 (Hardcoded)
    // 3. 给出分析结果 (根据模式区分)
    let aiResponseContent = '';
    
    if (reportMode.value === 'pro') {
        aiResponseContent = `已收到您的资料。经过深度智能分析，系统为您提取到以下关键维度：\n
报告主题：新技术应用及解释成果分析报告\n
分析对象：XX 预探井测井数据、新技术应用及解释成果\n
核心剖析维度：\n
新技术应用：聚焦 CMR 磁共振成像测井技术，剖析其在流体区分、孔隙结构识别中的应用成效。\n
解释成果：汇总测井解释层分类数据，查摆不同层位（油层、差油层、水层）的核心特征差异。\n
成果验证：结合邻井试油数据，验证本井解释成果的准确性，分析储层整体油气潜能。\n
优化建议：基于分析结果，提出试油、开发管控及参数标定的针对性改进建议。\n
系统已基于 “专业模式” 为您构建了严谨的逻辑框架，正在跳转至编辑器...
`;
    } else {
        // Open Mode (Default)
        aiResponseContent = `已收到您的资料。经过智能分析，为您提取到以下关键信息：\n
**报告主题**：2024年度领导班子民主生活会征求意见建议情况\n
**来源部门**：应用软件研究室\n
**核心分析维度**：\n
1. **政治纪律**：需加强理论学习深度，完善监督机制。\n
2. **党性作风**：需强化条例宣传，完善廉政长效监管。\n
3. **责任担当**：需加强廉洁教育系统性，优化任务分配机制。\n
4. **从严治党**：需提升政治责任领悟，增强网络主动发声意识。\n
系统已根据分析结果为您生成草稿，正在跳转至编辑器...`;
    }

    messages.value.push({ 
      role: 'ai', 
      content: aiResponseContent
    });
    scrollToBottom();
    
    // 4. 触发生成流程
    setTimeout(() => {
       isGenerating.value = true;
       generationStep.value = '正在构建文档结构...';
       
       setTimeout(() => {
           generationStep.value = '正在应用行业标准样式...';
       }, 800);

       setTimeout(() => {
           generationStep.value = '正在生成智能摘要...';
       }, 1600);

       setTimeout(() => {
           try {
             const newReportId = 'rpt_' + Date.now();
             // Select content based on mode
             let selectedContent = reportMode.value === 'pro' ? professionalSample : openSample;

             // Ensure content fallback
             const finalContent = selectedContent || '# 报告生成失败\n样本内容未能正确加载。';
             
             // Collect sources from user messages
             const allSources = [];
             messages.value.forEach(msg => {
                 if (msg.role === 'user' && msg.files && msg.files.length > 0) {
                     msg.files.forEach(f => allSources.push(f.name));
                 }
             });

             const newReport = {
                id: newReportId,
                title: '2024年度领导班子民主生活会征求意见建议情况报告',
                create_time: new Date().toLocaleDateString(),
                content: finalContent,
                sources: allSources
             };
             store.addReport(newReport);
             
             // Use replace instead of push to prevent back-navigation to generating state? 
             // Push is fine.
             router.push(`/editor/${newReportId}`).then(() => {
                 // Navigation success
                 // Component will unmount, so isGenerating doesn't matter much unless keep-alive
             }).catch(err => {
                 console.error('Navigation error:', err);
                 isGenerating.value = false;
                 alert('页面跳转失败: ' + err.message);
             });
           } catch (e) {
               console.error('Report creation failed:', e);
               isGenerating.value = false;
               alert('报告创建异常: ' + e.message);
           }
       }, 2200);

    }, 2500);

  }, 3000); // 模拟 3秒 思考时间
};

// 监听回车键
const onKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
};
</script>

<template>
  <div class="flex-1 flex flex-col h-full bg-slate-50 relative">

    <!-- Header -->
    <div class="h-16 flex items-center justify-center shrink-0">
      <h1 class="text-base font-medium text-slate-500">智能写作助手</h1>
    </div>
    
    <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 pt-10 space-y-6 hide-scrollbar">
      <div 
        v-for="(msg, index) in messages" 
        :key="index"
        class="flex flex-col gap-2 max-w-3xl mx-auto animate-fade-in"
        :class="msg.role === 'user' ? 'items-end' : 'items-start'"
      >
        <div v-if="msg.role === 'ai'" class="flex items-start gap-3">
          <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white shrink-0">
            <Icon icon="ri:robot-2-line" class="text-lg" />
          </div>
          <div class="bg-white p-4 rounded-2xl rounded-tl-none shadow-sm border border-slate-100">
            <div class="text-sm leading-relaxed text-slate-700 markdown-content" v-html="renderMarkdown(msg.content)"></div>
          </div>
        </div>

        <div v-else class="flex flex-col items-end gap-2 max-w-full">
          <!-- Files Display -->
          <div v-if="msg.files && msg.files.length > 0" class="flex flex-wrap justify-end gap-2 mb-1">
            <div 
              v-for="file in msg.files" 
              :key="file.id"
              class="relative border p-3 rounded-xl flex flex-col gap-1 w-[160px] text-left shadow-sm transition-transform hover:-translate-y-0.5"
              :class="[
                getFileStyle(file.type).bg, 
                getFileStyle(file.type).border,
                'cursor-pointer'
              ]"
              @click="openFilePreview(file)"
            >
               <div class="text-xs font-bold truncate" :class="getFileStyle(file.type).text" :title="file.name">
                 {{ file.name }}
               </div>
               <div class="flex items-center gap-1">
                 <div class="text-white text-[10px] font-bold px-1 py-0.5 rounded flex items-center gap-0.5 shrink-0" :class="getFileStyle(file.type).badge">
                   <Icon :icon="getFileStyle(file.type).icon" class="text-xs" />
                   {{ file.type }}
                 </div>
               </div>
            </div>
          </div>

          <!-- Text Content -->
          <div v-if="msg.content" class="bg-blue-600 text-white p-4 rounded-2xl rounded-tr-none shadow-sm shadow-blue-100">
            <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ msg.content }}</p>
          </div>
        </div>
      </div>
      <!-- Thinking Indicator -->
      <div v-if="isThinking" class="flex items-start gap-3 animate-fade-in max-w-3xl mx-auto mt-4">
         <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white shrink-0">
           <Icon icon="ri:robot-2-line" class="text-lg animate-pulse" />
         </div>
         <div class="bg-white p-4 rounded-2xl rounded-tl-none shadow-sm border border-slate-100 flex items-center">
           <span class="text-sm text-slate-500 mr-2">正在分析文档...</span>
           <div class="flex gap-1">
             <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
             <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
             <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
           </div>
         </div>
      </div>
    </div>

    <div class="p-6 shrink-0">
      <div class="max-w-3xl mx-auto">
        <div class="bg-white rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 p-3 relative transition-shadow focus-within:shadow-2xl focus-within:border-blue-100">
          
          <!-- File Preview -->
          <div v-if="uploadedFiles.length > 0" class="px-4 pt-4 flex flex-wrap gap-2">
            <div 
              v-for="(file, index) in uploadedFiles" 
              :key="file.id"
              class="relative rounded-xl p-3 flex flex-col gap-1 w-[160px] shadow-sm border group transition-all hover:shadow-md"
              :class="[
                getFileStyle(file.type).bg, 
                getFileStyle(file.type).border,
                'cursor-pointer'
              ]"
              @click="openFilePreview(file)"
            >
               <!-- Remove Button -->
               <button 
                 @click.stop="removeFile(file.id)"
                 class="absolute top-1 right-1 text-slate-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100 z-10"
               >
                 <Icon icon="material-symbols:close-rounded" />
               </button>

               <div class="text-xs font-bold truncate pr-4" :class="getFileStyle(file.type).text" :title="file.name">
                 {{ file.name }}
               </div>
               
               <div class="flex items-center gap-1.5 mt-1">
                 <div class="text-white text-[10px] font-bold px-1 py-0.5 rounded flex items-center gap-0.5 shrink-0" :class="getFileStyle(file.type).badge">
                   <Icon :icon="getFileStyle(file.type).icon" class="text-xs" />
                   {{ file.type }}
                 </div>
               </div>
            </div>
          </div>

          <div class="px-4 py-2">
            <textarea 
              ref="textareaRef"
              v-model="inputValue"
              @input="autoResize"
              @keydown="onKeydown"
              rows="1"
              class="w-full resize-none border-none focus:ring-0 text-slate-600 placeholder-slate-400 text-base py-1 bg-transparent outline-none max-h-[200px] overflow-y-auto hide-scrollbar" 
              placeholder="输入主题和写作要求..." 
            ></textarea>
          </div>
          
          <div class="flex items-center justify-between mt-2 px-2 pb-1">
            <div class="flex items-center gap-2 flex-wrap">
              <button 
                @click="triggerFileUpload"
                class="flex items-center gap-1.5 px-3 py-1.5 text-slate-600 hover:bg-slate-50 rounded-full text-sm font-medium transition-all border border-transparent hover:border-slate-200 group"
              >
                <Icon icon="ri:attachment-2" class="text-lg text-slate-400 group-hover:text-blue-500" />
                <span>参考资料</span>
              </button>
              
              <button 
                @click="showTemplateSelector = true"
                class="flex items-center gap-1.5 px-3 py-1.5 text-slate-600 hover:bg-slate-50 rounded-full text-sm font-medium transition-all border border-transparent hover:border-slate-200 group"
              >
                <Icon icon="ri:layout-grid-line" class="text-lg text-slate-400 group-hover:text-blue-500" />
                <span>从模板库选择</span>
              </button>
              

              <input 
                type="file" 
                ref="fileInput" 
                class="hidden" 
                multiple
                @change="handleFileSelect" 
              />
            </div>

            <!-- Report Mode Selector -->
            <div class="relative ml-auto mr-2">
                <button 
                  @click="showModeSelector = !showModeSelector"
                  class="flex items-center gap-1.5 px-3 py-1.5 hover:bg-slate-50 rounded-lg text-sm font-bold transition-all border border-transparent hover:border-slate-200 group text-slate-700"
                  :class="{'bg-slate-100': showModeSelector}"
                >
                  <span>{{ reportMode === 'pro' ? '专业' : '开放' }}</span>
                  <Icon icon="ri:arrow-down-s-line" class="text-slate-400 transition-transform duration-200" :class="{'rotate-180': showModeSelector}" />
                </button>

                <!-- Dropdown Menu -->
                <div v-if="showModeSelector" class="absolute bottom-full right-0 mb-2 w-72 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50 animate-fade-in origin-bottom-right">
                    <div class="p-2 space-y-1">
                        <div 
                           @click="handleSelectMode('pro')"
                           class="flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors"
                           :class="reportMode === 'pro' ? 'bg-blue-50' : 'hover:bg-gray-50'"
                        >
                            <div class="w-8 h-8 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center shrink-0 mt-0.5">
                                <Icon icon="ri:vip-diamond-fill" />
                            </div>
                            <div>
                                <div class="flex items-center gap-2">
                                    <span class="font-bold text-gray-800 text-sm">专业报告</span>
                                    <Icon v-if="reportMode === 'pro'" icon="ri:check-line" class="text-blue-600" />
                                </div>
                                <p class="text-xs text-gray-500 mt-1 leading-relaxed">擅长处理高阶数据分析，逻辑严密，思考时间更长</p>
                            </div>
                        </div>

                        <div 
                           @click="handleSelectMode('open')"
                           class="flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors"
                           :class="reportMode === 'open' ? 'bg-blue-50' : 'hover:bg-gray-50'"
                        >
                            <div class="w-8 h-8 rounded-lg bg-green-100 text-green-600 flex items-center justify-center shrink-0 mt-0.5">
                                <Icon icon="ri:flashlight-fill" />
                            </div>
                            <div>
                                <div class="flex items-center gap-2">
                                    <span class="font-bold text-gray-800 text-sm">开放报告</span>
                                    <Icon v-if="reportMode === 'open'" icon="ri:check-line" class="text-blue-600" />
                                </div>
                                <p class="text-xs text-gray-500 mt-1 leading-relaxed">快速生成通用型报告，适合日常汇报与总结</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Backdrop to close -->
                <div v-if="showModeSelector" @click="showModeSelector = false" class="fixed inset-0 z-40" style="background: transparent;"></div>
            </div>

            <button 
              @click="handleSend"
              :disabled="!inputValue.trim() && uploadedFiles.length === 0"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              :class="(inputValue.trim() || uploadedFiles.length > 0) ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700 hover:scale-105 active:scale-95' : 'bg-slate-100 text-slate-300'"
            >
              <span>发送</span>
              <Icon icon="ri:corner-down-left-line" class="text-base" />
            </button>
          </div>

        </div>
      </div>
    </div>


  <!-- Template Selector Modal -->
  <div v-if="showTemplateSelector" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
      <div class="bg-white w-full max-w-2xl h-[70vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-fade-in">
          <div class="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
              <h3 class="text-lg font-bold text-gray-800">选择模板</h3>
              <button class="p-2 hover:bg-gray-100 rounded-full text-gray-400 transition-colors" @click="showTemplateSelector = false">
                  <Icon icon="material-symbols:close-rounded" class="text-xl" />
              </button>
          </div>
          <div class="flex-1 overflow-y-auto p-4 space-y-6">
              <div v-for="(category, idx) in store.templates" :key="idx">
                  <h4 class="text-sm font-bold text-gray-500 mb-3 px-1">{{ category.name }}</h4>
                  <div class="grid grid-cols-2 gap-3">
                      <div 
                          v-for="template in category.list" 
                          :key="template.id"
                          @click="handleSelectTemplate(template)"
                          class="p-4 rounded-xl border border-gray-100 hover:border-blue-500 hover:bg-blue-50 cursor-pointer transition-all group"
                      >
                          <div class="font-bold text-gray-700 group-hover:text-blue-700 text-sm mb-1">{{ template.title }}</div>
                          <div class="text-xs text-gray-400">{{ template.create_time }}</div>
                      </div>
                  </div>
              </div>
          </div>
      </div>
  </div>

  <!-- Document Preview Modal -->
  <div v-if="showPreviewModal" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-[200] flex items-center justify-center p-4">
      <div class="bg-white w-full max-w-4xl h-[85vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-fade-in">
          <div class="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50 shrink-0">
              <div>
                  <h3 class="text-lg font-bold text-gray-900">{{ previewTitle }}</h3>
                  <p class="text-sm text-gray-500">模板预览</p>
              </div>
              <button class="p-2 hover:bg-gray-100 rounded-full text-gray-400 transition-colors" @click="showPreviewModal = false">
                  <Icon icon="material-symbols:close-rounded" class="text-xl" />
              </button>
          </div>
          <DocPreview :content="previewContent" class="flex-1 min-h-0 bg-gray-50" />
      </div>
  </div>

  <!-- Report Generation Transition Overlay -->
  <div v-if="isGenerating" class="fixed inset-0 bg-white z-[300] flex flex-col items-center justify-center animate-fade-in">
      <div class="w-16 h-16 mb-6 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-200">
          <Icon icon="ri:file-list-3-line" class="text-3xl text-white animate-pulse" />
      </div>
      <h2 class="text-xl font-bold text-slate-800 mb-2">正在生成报告...</h2>
      <p class="text-slate-500 text-sm animate-pulse">{{ generationStep }}</p>
      
      <!-- Progress Bar -->
      <div class="w-64 h-1.5 bg-slate-100 rounded-full mt-8 overflow-hidden">
          <div class="h-full bg-blue-600 rounded-full animate-progress" style="width: 100%; transition: width 2s linear; animation: progress 2s ease-in-out infinite;"></div>
      </div>
  </div>
  </div>
</template>

<style scoped>
/* 简单的淡入动画 */
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes progress {
  0% { transform: translateX(-100%); }
  50% { transform: translateX(0%); }
  100% { transform: translateX(100%); }
}

/* Markdown Styles for Chat */
.markdown-content :deep(p) {
  margin-bottom: 0.5em;
}
.markdown-content :deep(p):last-child {
  margin-bottom: 0;
}
.markdown-content :deep(strong) {
  font-weight: 600;
  color: #334155; /* slate-700 darker */
}
.markdown-content :deep(ul) {
  list-style-type: disc;
  padding-left: 1.25em;
  margin: 0.5em 0;
}
.markdown-content :deep(ol) {
  list-style-type: decimal;
  padding-left: 1.25em;
  margin: 0.5em 0;
}
.markdown-content :deep(li) {
  margin-bottom: 0.25em;
}
</style>