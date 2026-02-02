import MarkdownIt from 'markdown-it';
import markdownItKatex from 'markdown-it-katex';

// 初始化 markdown-it 实例
const md = new MarkdownIt({
  html: true,       // 允许 HTML 标签
  breaks: true,     // 换行符转换为 <br>
  linkify: true     // 自动识别链接
});

md.use(markdownItKatex);

// 自定义渲染规则（可选）：比如让表格更好看
// 这里我们可以简单保持默认，因为我们会在 CSS 里修饰它
export function renderMarkdown(text) {
  return md.render(text || '');
}