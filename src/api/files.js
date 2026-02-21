import { API_BASE_URL } from './config';

/**
 * 上传单个文件到后端并解析内容
 * @param {File} file
 * @returns {Promise<{file_id: string, name: string, content_type: string, text: string, summary?: string}>}
 */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const resp = await fetch(`${API_BASE_URL}/files/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!resp.ok) {
    let detail = '';
    try {
      const data = await resp.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      detail = await resp.text();
    }
    throw new Error(`文件上传失败 (${resp.status}): ${detail}`);
  }

  return resp.json();
}

