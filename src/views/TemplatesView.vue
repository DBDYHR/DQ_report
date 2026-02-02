<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- 顶部工具栏 -->
    <div class="shrink-0 px-10 pt-10 pb-4 flex justify-between items-center">
      <div class="flex items-center gap-3">
        <h1 class="text-2xl font-bold text-gray-800">模板库</h1>
        <span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold">
          {{ totalTemplates }}
        </span>
      </div>
      
      <div class="flex gap-3">
        <button 
          @click="showAnalysisModal = true"
          class="bg-white border border-gray-200 text-gray-700 hover:border-blue-400 hover:text-blue-600 px-5 py-2.5 rounded-xl font-semibold flex items-center gap-2 transition-all shadow-sm"
        >
          <Icon icon="material-symbols:magic-button-outline" class="text-lg" />
          智能解析
        </button>
        <button 
          @click="openNewTemplate"
          class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-semibold flex items-center gap-2 transition-all shadow-md"
        >
          <Icon icon="material-symbols:add-rounded" class="text-lg" />
          新建模板
        </button>
      </div>
    </div>

    <!-- 可滚动内容区：模板列表 -->
    <div class="flex-1 overflow-y-auto px-10 pb-10">
      <div class="space-y-10">
        <div v-for="(category, index) in store.templates" :key="index">
          <h2 class="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <Icon icon="material-symbols:folder-open-outline" class="text-xl" />
            {{ category.name }}
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              v-for="template in category.list" 
              :key="template.id"
              class="group bg-white rounded-2xl p-6 shadow-sm border border-slate-100 hover:shadow-md hover:border-blue-200 transition-all cursor-pointer relative overflow-hidden"
            >
              <!-- Decorative gradient top -->
              <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-400 to-indigo-400"></div>

              <div class="flex justify-between items-start mb-4">
                <div class="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                  <Icon icon="material-symbols:description-outline" class="text-xl" />
                </div>
                <!-- Actions (visible on hover) -->
                <div class="opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                   <button 
                    class="p-2 hover:bg-slate-100 rounded-lg text-slate-500 hover:text-red-500 transition-colors"
                    title="删除模板"
                    @click.stop="confirmDelete(template.id)"
                  >
                    <Icon icon="material-symbols:delete-outline" class="text-lg" />
                  </button>
                </div>
              </div>

              <h3 class="font-bold text-slate-800 mb-2 group-hover:text-blue-600 transition-colors">
                {{ template.title }}
              </h3>
              
              <p class="text-slate-500 text-sm mb-6 line-clamp-2">
                创建于: {{ template.create_time }}
              </p>

              <button 
                @click.stop="openPreview(template)"
                class="w-full py-2.5 rounded-xl border border-slate-200 text-slate-600 font-medium text-sm hover:border-blue-600 hover:text-blue-600 hover:bg-blue-50 transition-all flex items-center justify-center gap-2"
              >
                <span>预览模板</span>
                <Icon icon="material-symbols:visibility-outline" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Smart Analysis Modal -->
  <div v-if="showAnalysisModal" class="fixed inset-0 bg-blue-900/20 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white w-[500px] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-modal">
      <div class="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
        <h3 class="text-lg font-bold text-gray-900">解析文件以创建模板</h3>
        <button class="p-2 hover:bg-gray-100 rounded-full text-gray-400 transition-colors" @click="showAnalysisModal = false">
          <Icon icon="material-symbols:close-rounded" class="text-xl" />
        </button>
      </div>
      <div class="p-8">
        <div 
          v-if="!isAnalyzing"
          class="border-2 border-dashed border-blue-200 rounded-xl bg-blue-50/30 p-10 flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all group"
          @click="triggerFileUpload"
        >
          <div class="w-14 h-14 bg-white rounded-full shadow-sm flex items-center justify-center mb-4 text-blue-500 group-hover:scale-110 transition-transform">
              <Icon icon="ri:upload-cloud-2-line" class="text-3xl" />
          </div>
          <p class="text-blue-600 font-bold text-base group-hover:underline decoration-2 underline-offset-4">点击上传文档</p>
          <input 
            type="file" 
            ref="fileInput" 
            class="hidden" 
            accept=".pdf,.docx,.txt" 
            @change="handleFileSelected"
          />
        </div>
        
        <div v-else class="py-8 flex flex-col items-center">
            <Icon icon="ri:loader-4-line" class="text-4xl text-blue-600 animate-spin mb-4" />
            <p class="text-gray-800 font-bold">正在分析结构...</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Template Preview Modal -->
  <div v-if="showPreviewModal && selectedTemplate" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white w-full max-w-4xl h-[85vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-modal">
          <div class="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50 shrink-0">
              <div>
                  <h3 class="text-lg font-bold text-gray-900">{{ selectedTemplate.title }}</h3>
                  <p class="text-sm text-gray-500">预览模式</p>
              </div>
              <div class="flex gap-3">
                  <button class="px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg transition-colors" @click="closePreview">
                      取消
                  </button>
                  <button class="px-5 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 shadow-md transition-colors" @click="editTemplate">
                      <Icon icon="ri:edit-box-line" class="inline text-lg mr-1"/> 编辑模板
                  </button>
              </div>
          </div>
          <DocPreview :content="selectedTemplate.content" class="flex-1 min-h-0 bg-gray-50" />
      </div>
  </div>

  <!-- Delete Confirmation Modal -->
  <ConfirmModal 
    :show="showDeleteModal"
    title="删除模板"
    content="确定要删除这个模板吗？删除后将无法恢复。"
    @close="showDeleteModal = false"
    @confirm="handleDeleteConfirm"
  />

  <!-- 选择模板所属大类 Modal -->
  <div v-if="showCategoryModal" class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/80">
        <div class="flex items-center gap-2">
          <Icon icon="material-symbols:category-outline" class="text-xl text-blue-600" />
          <h3 class="text-base font-bold text-gray-900">选择模板所属大类</h3>
        </div>
        <button class="p-1.5 rounded-full hover:bg-gray-100 text-gray-400" @click="cancelCategory">
          <Icon icon="material-symbols:close-rounded" class="text-xl" />
        </button>
      </div>
      <div class="px-6 py-6 space-y-4">
        <p class="text-sm text-gray-600">
          请为新创建的模板选择一个所属的大类，便于在模板库中分类管理。
        </p>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-gray-500 mb-2">选择已有大类</label>
            <select
              v-model="selectedCategoryName"
              class="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option
                v-for="(category, idx) in store.templates"
                :key="idx"
                :value="category.name"
              >
                {{ category.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-500 mb-1">或新建一个大类</label>
            <input
              v-model="newCategoryName"
              type="text"
              placeholder="输入新的大类名称（如：专项汇报模板）"
              class="w-full border border-dashed border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 placeholder:text-gray-400"
            />
            <p class="mt-1 text-[11px] text-gray-400">
              如同时填写新大类名称，则优先使用新名称创建分类。
            </p>
          </div>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3 bg-gray-50/60">
        <button
          class="px-4 py-2 rounded-xl border border-gray-300 text-gray-600 text-sm font-medium hover:bg-white"
          @click="cancelCategory"
        >
          取消
        </button>
        <button
          class="px-5 py-2 rounded-xl bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700"
          @click="confirmCategory"
        >
          确认并创建
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { Icon } from '@iconify/vue';
import { useReportStore } from '../stores/useReportStore';
import { useRouter } from 'vue-router';
import DocPreview from '../components/editor/DocPreview.vue';
import ConfirmModal from '../components/common/ConfirmModal.vue';

const store = useReportStore();
const router = useRouter();

const totalTemplates = computed(() => {
  return store.templates.reduce((acc, curr) => acc + curr.list.length, 0);
});

// Smart Analysis Logic
const showAnalysisModal = ref(false);
const isAnalyzing = ref(false);

const fileInput = ref(null);

// 新建模板时选择 / 创建所属大类
const showCategoryModal = ref(false);
const selectedCategoryName = ref('');
const newCategoryName = ref('');
const pendingTemplate = ref(null);

const triggerFileUpload = () => {
    fileInput.value.click();
};

const handleFileSelected = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    // 开始模拟分析
    startAnalysis();
    
    // 清空 input 以便下次能选同一个文件
    event.target.value = '';
};

const startAnalysis = () => {
    isAnalyzing.value = true;
    
    // 模拟解析过程
    setTimeout(() => {
        isAnalyzing.value = false;
        showAnalysisModal.value = false;
        
        // 解析成功后，创建一个新的临时模板ID，并在 Editor 中打开
        // 这里我们预设一些解析出来的内容
        const mockParsedContent = `# 报告模板

**单位：**
**时间：**

## 目 录
一、概况
二、测井内容及质量评定
三、测井解释参数
四、新技术应用情况
五、解释成果及分析
六、建议及要求
七、图、表目录
八、附带说明

## 一、概况

| 类别 | 项目/参数 | 内容 | 项目/参数 | 内容 |
| :--- | :--- | :--- | :--- | :--- |
| **钻井** | 井别 | | 井位 | |
| | 钻井目的 | | | |
| | 钻井队 | | 开钻时间 | |
| | 套管程序 | | 钻头程序 | |
| | 完钻时间 | | 完钻井深 | |
| | 钻开油层时间 | | 钻井液停止循环时间 | |
| **钻井液** | 密度 | | 粘度 | |
| | 失水量 | | pH 值 | |
| | 矿化度 | | 电阻率 | |
| | 样品来源 | | | |
| **测井** | 测井小队 | | 测井系列 | |
| | 测井时间 | | 测时井深 | |
| | 测量井段 | | 井底温度 | |

二、测井内容及质量评定
### 1. 测井曲线施工质量评价

| 序号 | 曲线名称 | 测量井段 (m) | 质量评比 | 深度比例 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | | | | | |
| 2 | | | | | |
| ... | | | | | |
| **合格率** | | | | | |

**填写说明：**
1. 质量评比栏以合格、优质、不合格注明。
2. 备注栏注明质量不合格的原因。

### 2. 测井曲线应用质量评价

| 序号 | 曲线名称 | 测量井段 (m) | 质量评比 | 深度比例 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | | | | | |
| 2 | | | | | |
| ... | | | | | |
| **合格率** | | | | |  |

**填写说明：**
1. 质量评比栏以合格、优质、不合格注明。
2. 备注栏注明质量不合格的原因。

## 三、测井解释参数

### 1. 处理程序及参数选取依据

### 2. 参数选取结果
**井段：**
| 成分/项 | UOIL | XOIL | UWAT | XWAT | SAND | SHAL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RHOB** | | | | | | |
| **NPHI** | | | | | | |
| **DT** | | | | | | |
| **RXO** | | | | | | |
| **RT** | | | | | | |
| **GR** | | | | | | |
## 四、新技术应用情况
填写说明：XXXX

## 五、解释成果及分析
### 1. 解释成果
### 2. 解释成果分析
#### 2.1 概述

#### 2.2 邻井试油情况
#### 2.3 分层讨论
## 六、建议及要求
## 七、图、表目录
| 序号 | 图（表）件名称 | 份数 |
| :--- | :--- | :--- |
| 1 | | 1 |
| 2 | | |
| ... | | |

## 八、附带说明
1. 处理程序及说明/处理解释参数符号说明
2. 成果图展示/简介
![图1-井位示意图](图占位)`;

        const newId = 'tpl_' + Date.now();
        
        const newTemplate = {
            id: newId,
            title: '智能解析结果 - ' + new Date().toLocaleTimeString(),
            create_time: new Date().toLocaleDateString(),
            content: mockParsedContent
        };

        // 先缓存模板信息，弹出所属大类选择框
        pendingTemplate.value = newTemplate;
        // 默认选中第一个分类
        selectedCategoryName.value = store.templates[0]?.name || '';
        newCategoryName.value = '';
        showCategoryModal.value = true;
        
    }, 2000);
};

const openNewTemplate = () => {
    const newId = 'tpl_' + Date.now();
    // 生成一个空模板，等待用户选择所属大类后再真正加入
    const newTemplate = {
        id: newId,
        title: '新建模板',
        create_time: new Date().toLocaleDateString(),
        content: '# 新模板\n请在此处编辑模板内容...'
    };
    pendingTemplate.value = newTemplate;
    selectedCategoryName.value = store.templates[0]?.name || '';
    newCategoryName.value = '';
    showCategoryModal.value = true;
};

// Preview Logic
const showPreviewModal = ref(false);
const selectedTemplate = ref(null);

const openPreview = (template) => {
    selectedTemplate.value = template;
    showPreviewModal.value = true;
};

const closePreview = () => {
    showPreviewModal.value = false;
    selectedTemplate.value = null;
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
        store.deleteTemplate(itemToDelete.value);
        showDeleteModal.value = false;
        itemToDelete.value = null;
    }
};

const editTemplate = () => {
    const tpl = selectedTemplate.value;
    closePreview();
    router.push(`/editor/${tpl.id}?mode=template`); 
};

// 确认选择模板所属大类
const confirmCategory = () => {
    if (!pendingTemplate.value) {
        showCategoryModal.value = false;
        return;
    }
    // 优先使用用户输入的新大类名称
    const inputName = newCategoryName.value.trim();
    let targetCategoryName = inputName || selectedCategoryName.value || store.templates[0]?.name;

    // 如果输入了新名称且当前不存在该分类，则创建一个新大类
    const existed = store.templates.find(cat => cat.name === targetCategoryName);
    if (!existed) {
        store.templates.push({
            name: targetCategoryName,
            list: []
        });
    }

    store.addTemplate(pendingTemplate.value, targetCategoryName);

    // 跳转到编辑页
    router.push(`/editor/${pendingTemplate.value.id}?mode=template`);

    // 重置状态
    pendingTemplate.value = null;
    newCategoryName.value = '';
    showCategoryModal.value = false;
};

const cancelCategory = () => {
    pendingTemplate.value = null;
    newCategoryName.value = '';
    showCategoryModal.value = false;
};

</script>
