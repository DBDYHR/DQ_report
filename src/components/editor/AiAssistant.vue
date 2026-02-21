<script setup>
import { ref, nextTick } from 'vue';
import { Icon } from '@iconify/vue';
import { generateOpenReport } from '../../api/ai';

// 接收父组件的内容 (v-model)、模式和标题
const props = defineProps({
  modelValue: { type: String, default: '' }, // 编辑器的内容
  mode: { type: String, default: 'report' }, // 模式：'template' 或 'report'
  title: { type: String, default: '' },      // 当前报告标题
});

const emit = defineEmits(['update:modelValue']);

// 状态
const inputVal = ref('');
const isThinking = ref(false);
const chatContainer = ref(null);
const messages = ref([
  {
    role: 'ai',
    content:
      '你好！我是你的报告助手。<br>我可以调用后端大模型，帮你扩写内容、润色语气或重构章节结构。',
  },
]);

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

// 流式输出回复逻辑（仅对短提示做打字效果，正文更新直接写回编辑器）
const startStreamingReply = (fullText, contentUpdate) => {
  const aiMsg = { role: 'ai', content: '' };
  messages.value.push(aiMsg);
  const reactiveMsg = messages.value[messages.value.length - 1];

  let i = 0;
  const totalLength = fullText.length;

  const intervalId = setInterval(() => {
    const chunkSize = Math.floor(Math.random() * 6) + 3; // 3-8 字
    const chunk = fullText.substring(i, i + chunkSize);

    if (reactiveMsg) {
      reactiveMsg.content += chunk;
    }
    i += chunkSize;
    scrollToBottom();

    if (i >= totalLength) {
      clearInterval(intervalId);
      scrollToBottom();

      if (contentUpdate) {
        // 在提示输出完后更新编辑器内容
        setTimeout(() => {
          emit('update:modelValue', contentUpdate);
        }, 400);
      }
    }
  }, 40);
};

// 发送消息核心逻辑：真正调用后端 AI
const sendMessage = async () => {
  const text = inputVal.value.trim();
  if (!text || isThinking.value) return;

  // 1. 用户消息上屏
  messages.value.push({ role: 'user', content: text });
  inputVal.value = '';
  isThinking.value = true;
  await scrollToBottom();

  try {
    const payload = {
      task_type: 'open_report',
      title: props.title || undefined,
      outline: undefined,
      draft: props.modelValue || '',
      materials: [], // 目前未接入材料，后续可由 ChatMode / Wizard 传入
      user_config: {
        instruction: text,
      },
    };

    const { content } = await generateOpenReport(payload);

    isThinking.value = false;

    const tip =
      '已根据你的指令调用后端大模型，对当前报告进行了生成 / 润色，编辑区内容已自动更新。';

    // 不在对话里展开整篇报告，只提示 + 更新正文
    startStreamingReply(tip, content || props.modelValue);
  } catch (err) {
    console.error('AI 调用失败:', err);
    isThinking.value = false;

    const errorMsg =
      '调用后端 AI 接口失败，请稍后重试，或检查服务是否已启动。<br><small>' +
      (err?.message || String(err)) +
      '</small>';

    startStreamingReply(errorMsg, null);
  }
};
</script>

<template>
  <div class="flex flex-col h-full bg-white border border-indigo-100 rounded-xl shadow-sm overflow-hidden ring-1 ring-indigo-50">
    <div class="h-10 bg-indigo-50/50 border-b border-indigo-100 px-4 flex items-center justify-between shrink-0">
      <span class="text-xs font-bold text-indigo-600 flex items-center gap-2">
        <Icon icon="ri:sparkling-fill" /> AI 智能助手
      </span>
      <span class="text-[10px] text-indigo-400">现在已接入后端大模型，可输入具体修改指令</span>
    </div>

    <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-3 bg-white hide-scrollbar">
      <div 
        v-for="(msg, index) in messages" 
        :key="index"
        :class="[
          'max-w-[85%] px-3 py-2 rounded-xl text-sm leading-relaxed text-justify break-words shadow-sm',
          msg.role === 'user' 
            ? 'bg-blue-50 text-blue-700 self-end ml-auto rounded-tr-none' 
            : 'bg-gray-50 text-gray-700 border border-gray-100 rounded-tl-none'
        ]"
      >
        <div v-html="msg.content"></div>
      </div>

      <div v-if="isThinking" class="bg-gray-50 border border-gray-100 px-3 py-2 rounded-xl rounded-tl-none w-fit">
        <div class="flex items-center gap-1">
          <Icon icon="ri:brain-line" class="text-gray-400 text-xs mr-1" />
          <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
          <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-100"></span>
          <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-200"></span>
        </div>
      </div>
    </div>

    <div class="p-3 border-t border-gray-100 bg-gray-50 shrink-0">
      <div class="relative">
        <input 
          v-model="inputVal"
          @keydown.enter="sendMessage"
          type="text" 
          placeholder="给 AI 发送指令..." 
          class="w-full pl-4 pr-10 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-50 transition-all"
        />
        <button 
          @click="sendMessage"
          class="absolute right-1 top-1 w-8 h-8 flex items-center justify-center bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors shadow-sm"
        >
          <Icon icon="ri:send-plane-fill" class="text-sm" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 简单的打字机动画延迟 */
.delay-100 { animation-delay: 0.1s; }
.delay-200 { animation-delay: 0.2s; }
</style>