<script setup>
import { Icon } from '@iconify/vue';
import { useRouter, useRoute } from 'vue-router';
import { ref } from 'vue';

const router = useRouter();
const route = useRoute();
const isCollapsed = ref(false);

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

// 简单的导航函数
const navigateTo = (path) => {
  router.push(path);
};

// 检查当前路由是否匹配 (用于高亮菜单)
const isActive = (path) => route.path === path;
</script>

<template>
  <aside 
    class="bg-white border-r border-slate-200 flex flex-col shrink-0 z-50 h-screen transition-all duration-300 relative group/sidebar"
    :class="[isCollapsed ? 'w-20' : 'w-64']"
  >
    <!-- 顶部 Logo 区域 -->
    <div class="px-5 py-4 border-b border-slate-100 flex items-center shrink-0 overflow-hidden whitespace-nowrap h-16 transition-all duration-300 gap-0">
      
      <!-- 汉堡菜单 (切换) (固定位置: pl-5 = 20px, btn-center = 20px -> 40px Axis) -->
      <button 
        @click="toggleSidebar"
        class="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition-colors shrink-0"
      >
        <Icon icon="material-symbols:menu-rounded" class="text-2xl" />
      </button>

      <!-- Logo & 标题 (收缩时隐藏) -->
      <div 
         class="flex items-center gap-3 overflow-hidden transition-all duration-300 ease-in-out ml-3"
         :class="[isCollapsed ? 'w-0 opacity-0' : 'w-40 opacity-100']"
      >
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white shadow-sm shrink-0">
          <Icon icon="material-symbols:edit-document-outline-sharp" class="text-xl" />
        </div>
        <h1 class="font-bold text-lg tracking-tight text-slate-800 truncate">
          AI写作助手
        </h1>
      </div>
    </div>

    <!-- 主要内容区域 (统一容器 px-5 = 20px) -->
    <div class="flex-1 overflow-y-auto py-4 flex flex-col gap-6 hide-scrollbar overflow-x-hidden">
      
      <!-- 新建按钮 -->
      <div class="px-5 transition-all duration-300">
        <button 
          @click="navigateTo('/chat')"
          class="w-full flex items-center hover:bg-slate-50 text-slate-700 rounded-xl transition-all duration-300 font-medium text-sm group relative overflow-hidden whitespace-nowrap py-2.5 pl-2 border border-slate-200"
          :class="[isCollapsed ? 'gap-0 border-transparent' : 'gap-2']"
          :title="isCollapsed ? '开启新报告' : ''"
        >
          <!-- 图标容器 (w-6 = 24px) -->
          <div class="w-6 h-6 flex items-center justify-center shrink-0">
            <Icon icon="material-symbols:add-rounded" class="text-xl text-slate-500 group-hover:text-slate-800 transition-transform duration-300" />
          </div>
          <!-- 文本 -->
          <span 
            class="transition-all duration-300 overflow-hidden"
            :class="[isCollapsed ? 'w-0 opacity-0' : 'w-24 opacity-100']"
          >
            开启新报告
          </span>
        </button>
      </div>

      <!-- 导航菜单 -->
      <nav class="px-5 space-y-1">
        <!-- 标题 / 分割线 容器 (固定高度 h-8, mb-2) -->
        <div class="relative h-8 flex items-center mb-2 px-2">
          <!-- 文字标题 (展开显示) -->
          <p 
            class="absolute left-2 text-xs font-semibold text-slate-400 uppercase tracking-wider transition-opacity duration-300 whitespace-nowrap overflow-hidden"
            :class="[isCollapsed ? 'opacity-0 delay-0' : 'opacity-100 delay-100']"
          >
            功能导航
          </p>
          <!-- 分割线 (收缩显示) -->
          <div 
             class="absolute left-0 right-0 h-px bg-slate-200 transition-opacity duration-300"
             :class="[isCollapsed ? 'opacity-100 delay-100' : 'opacity-0 delay-0']"
          ></div>
        </div>
        
        <button 
          @click="navigateTo('/templates')"
          :class="[
            'w-full flex items-center rounded-lg transition-all duration-300 text-sm font-medium text-left relative overflow-hidden whitespace-nowrap py-2.5 pl-2',
            isActive('/templates') 
              ? 'bg-blue-50 text-blue-700' 
              : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900',
            isCollapsed ? 'gap-0' : 'gap-3'
          ]"
          :title="isCollapsed ? '模板管理' : ''"
        >
          <div class="w-6 h-6 flex items-center justify-center shrink-0">
            <Icon 
              icon="material-symbols:dashboard-customize-outline" 
              class="text-lg transition-transform duration-300"
              :class="isActive('/templates') ? 'text-blue-600' : 'text-slate-400'"
            />
          </div>
          <span 
             class="transition-all duration-300 overflow-hidden"
             :class="[isCollapsed ? 'w-0 opacity-0' : 'w-32 opacity-100']"
          >
            模板管理
          </span>
        </button>

        <button 
          @click="navigateTo('/platform')"
          class="w-full flex items-center rounded-lg transition-all duration-300 text-sm font-medium text-left text-slate-600 hover:bg-slate-50 hover:text-slate-900 relative overflow-hidden whitespace-nowrap py-2.5 pl-2"
          :class="[isCollapsed ? 'gap-0' : 'gap-3']"
          :title="isCollapsed ? '我的报告' : ''"
        >
          <div class="w-6 h-6 flex items-center justify-center shrink-0">
            <Icon icon="material-symbols:auto-awesome-motion-outline" class="text-lg text-slate-400 duration-300" />
          </div>
          <span 
             class="transition-all duration-300 overflow-hidden"
             :class="[isCollapsed ? 'w-0 opacity-0' : 'w-32 opacity-100']"
          >
            我的报告
          </span>
        </button>
      </nav>

      <div class="border-t border-slate-100 mx-5 transition-all duration-300"></div>

    </div>

    <!-- 底部用户信息 (px-5 = 20px) -->
    <div class="px-5 py-4 border-t border-slate-100 shrink-0 whitespace-nowrap overflow-hidden">
      <div 
        class="flex items-center rounded-xl hover:bg-slate-50 cursor-pointer transition-all duration-300 py-2 pl-1"
        :class="[isCollapsed ? 'gap-0' : 'gap-3']"
        :title="isCollapsed ? '个人中心' : ''"
      >
        <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center overflow-hidden shrink-0">
          <img 
            alt="User" 
            class="w-full h-full object-cover" 
            src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
          />
        </div>
        <div 
          class="flex-1 min-w-0 transition-all duration-300 overflow-hidden"
           :class="[isCollapsed ? 'w-0 opacity-0' : 'w-32 opacity-100']"
        >
          <p class="text-sm font-medium text-slate-700 truncate">高级分析师</p>
          <p class="text-xs text-slate-500 truncate">user@example.com</p>
        </div>
      </div>
    </div>
  </aside>
</template>