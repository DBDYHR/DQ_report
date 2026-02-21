import { API_BASE_URL } from './config';

/**
 * 检索报告相关材料（生成前一步，供用户确认）
 * @param {object} payload 与 open-report 相同的 payload 结构
 * @returns {Promise<{query: string, results: Array<{title, snippet, url}>}>}
 */
export async function searchForReport(payload) {
  const resp = await fetch(`${API_BASE_URL}/ai/search-for-report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    let detail = '';
    try {
      const data = await resp.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      detail = await resp.text();
    }
    throw new Error(`检索接口调用失败 (${resp.status}): ${detail}`);
  }

  return resp.json();
}

/**
 * 调用后端开放报告写作接口
 * @param {object} payload OpenReportRequest 对象，可含 search_results 预取结果
 * @returns {Promise<{content: string}>}
 */
export async function generateOpenReport(payload) {
  const resp = await fetch(`${API_BASE_URL}/ai/open-report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    let detail = '';
    try {
      const data = await resp.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      detail = await resp.text();
    }
    throw new Error(`AI 接口调用失败 (${resp.status}): ${detail}`);
  }

  return resp.json();
}

