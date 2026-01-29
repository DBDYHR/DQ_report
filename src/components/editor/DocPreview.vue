<script setup>
import { computed } from 'vue';
import { Icon } from '@iconify/vue';
import { renderMarkdown } from '../../utils/markdown';

const props = defineProps({
  content: { type: String, default: '' },
  fontFamily: { type: String, default: '"SimSun", "Songti SC", serif' },
  sources: { type: Array, default: () => [] }
});

// 实时计算 HTML
const htmlContent = computed(() => renderMarkdown(props.content));
</script>

<template>
  <div class="w-full h-full overflow-y-auto bg-gray-100/50 py-8 scroll-smooth">
    <div class="mx-auto bg-white shadow-xl w-full max-w-[210mm] min-h-[297mm] p-8 md:p-[20mm] origin-top h-auto">
      <div 
        class="prose-preview" 
        :style="{ fontFamily: props.fontFamily }"
        v-html="htmlContent"
      ></div>

      <!-- Sources Display (Bottom) -->
      <div v-if="props.sources && props.sources.length > 0" class="mt-12 pt-8 border-t border-dashed border-gray-200 print:hidden">
         <div class="text-xs font-bold text-gray-400 mb-4 flex items-center gap-1.5 ">
            <Icon icon="ri:links-line" /> 报告参考来源
         </div>
         <div class="flex flex-col gap-2">
            <div v-for="(file, idx) in props.sources" :key="idx" class="flex items-center gap-2 text-xs text-gray-600 bg-gray-50 px-3 py-2.5 rounded border border-gray-100 max-w-md">
               <Icon icon="ri:file-text-line" class="text-blue-500 text-lg" />
               <span class="font-medium truncate">{{ file }}</span>
            </div>
         </div>
      </div>
    </div>
  </div>
</template>

<style>
/* 复刻原项目的文档样式 */
.prose-preview {
  font-family: "SimSun", "Songti SC", serif; /* 仿宋风格 */
  color: #000;
  line-height: 1.8;
  word-wrap: break-word;
}

.prose-preview h1 { font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0; }
.prose-preview h2 { font-size: 18px; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 4px; margin-top: 24px; }
.prose-preview h3 { font-size: 16px; font-weight: bold; margin-top: 18px; }
.prose-preview p { margin-bottom: 12px; text-align: justify; }

/* 表格样式 */
.prose-preview table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 14px; font-family: sans-serif; }
.prose-preview th, .prose-preview td { border: 1px solid #000; padding: 8px; text-align: center; }
.prose-preview th { background-color: #f2f2f2; font-weight: bold; }

/* 引用块 */
.prose-preview blockquote { border-left: 4px solid #ccc; padding-left: 10px; color: #666; font-style: italic; margin: 10px 0; }
</style>