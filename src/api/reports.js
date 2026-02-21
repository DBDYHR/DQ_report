import { API_BASE_URL } from './config';

/**
 * 创建一篇新报告
 * @param {{title: string, type?: string, content: string, sources?: string[]}} payload
 * @returns {Promise<any>} 后端返回的完整 Report 对象
 */
export async function createReport(payload) {
  const body = {
    title: payload.title,
    type: payload.type || 'open_report',
    content: payload.content,
    sources: payload.sources || [],
  };

  const resp = await fetch(`${API_BASE_URL}/reports`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    let detail = '';
    try {
      const data = await resp.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      detail = await resp.text();
    }
    throw new Error(`创建报告失败 (${resp.status}): ${detail}`);
  }

  return resp.json();
}

// 更新已有报告（部分字段）
export async function updateReport(id, payload) {
  const resp = await fetch(`${API_BASE_URL}/reports/${encodeURIComponent(id)}`, {
    method: 'PUT',
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
    throw new Error(`更新报告失败 (${resp.status}): ${detail}`);
  }

  return resp.json();
}

// 删除报告
export async function deleteReport(id) {
  const resp = await fetch(`${API_BASE_URL}/reports/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });

  if (!resp.ok && resp.status !== 204) {
    let detail = '';
    try {
      const data = await resp.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      detail = await resp.text();
    }
    throw new Error(`删除报告失败 (${resp.status}): ${detail}`);
  }
}

// 预留：后续可用于 PlatformMode / Editor 初始化
export async function listReports() {
  const resp = await fetch(`${API_BASE_URL}/reports`);
  if (!resp.ok) {
    throw new Error(`获取报告列表失败 (${resp.status})`);
  }
  return resp.json();
}

export async function getReport(id) {
  const resp = await fetch(`${API_BASE_URL}/reports/${encodeURIComponent(id)}`);
  if (!resp.ok) {
    throw new Error(`获取报告失败 (${resp.status})`);
  }
  return resp.json();
}

