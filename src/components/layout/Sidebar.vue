<script setup>
import { Icon } from '@iconify/vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

// 简单的导航函数
const navigateTo = (path) => {
  router.push(path);
};

// 检查当前路由是否匹配 (用于高亮菜单)
const isActive = (path) => route.path === path;
</script>

<template>
  <aside class="w-64 bg-white border-r border-slate-200 flex flex-col shrink-0 z-50 h-screen transition-all">
    <div class="p-4 border-b border-slate-100 flex items-center gap-2 h-16 shrink-0">
      <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white shadow-sm">
        <Icon icon="material-symbols:edit-document-outline-sharp" class="text-xl" />
      </div>
      <h1 class="font-bold text-lg tracking-tight text-slate-800">AI写作助手</h1>
    </div>

    <div class="flex-1 overflow-y-auto py-4 flex flex-col gap-6 hide-scrollbar">
      
      <div class="px-4">
        <button 
          @click="navigateTo('/new-report')"
          class="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition-all font-medium text-sm group"
        >
          <Icon icon="material-symbols:add-rounded" class="text-xl text-slate-500 group-hover:text-slate-800" />
          新建报告
        </button>
      </div>

      <nav class="px-2 space-y-1">
        <p class="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">功能导航</p>
        
        <button 
          @click="navigateTo('/templates')"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm font-medium text-left',
            isActive('/templates') 
              ? 'bg-blue-50 text-blue-700' 
              : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
          ]"
        >
          <Icon 
            icon="material-symbols:dashboard-customize-outline" 
            class="text-lg"
            :class="isActive('/templates') ? 'text-blue-600' : 'text-slate-400'"
          />
          模板管理
        </button>

        <button 
          @click="navigateTo('/platform')"
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm font-medium text-left text-slate-600 hover:bg-slate-50 hover:text-slate-900"
        >
          <Icon icon="material-symbols:auto-awesome-motion-outline" class="text-lg text-slate-400" />
          我的报告
        </button>
      </nav>

      <div class="border-t border-slate-100 mx-4"></div>

    </div>

    <div class="p-4 border-t border-slate-100 shrink-0">
      <div class="flex items-center gap-3 p-2 rounded-xl hover:bg-slate-50 cursor-pointer transition-colors">
        <div class="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center overflow-hidden shrink-0">
          <img 
            alt="User" 
            class="w-full h-full object-cover" 
            src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
          />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-700 truncate">高级分析师</p>
          <p class="text-xs text-slate-500 truncate">user@example.com</p>
        </div>
      </div>
    </div>
  </aside>
</template>