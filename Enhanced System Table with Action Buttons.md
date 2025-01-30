テーブルの各行にボタンを設置しつつ、UIをクリーンに保つためのアプローチを提案させていただきます。



```plaintext
import React, { useState } from 'react';
import { Eye, Edit2, Copy } from 'lucide-react';

const SystemTable = () => {
  const [openWindows, setOpenWindows] = useState(new Set());
  const [openSystemIds, setOpenSystemIds] = useState(new Set());

  // サンプルデータ
  const systemData = [
    { id: 1, name: "System A" },
    { id: 2, name: "System B" },
    { id: 3, name: "System C" }
  ];

  const openChildWindow = (systemId, action) => {
    const childWindow = window.open(
      `/child-page/${systemId}?action=${action}`,
      `system-${systemId}-${action}`,
      'width=800,height=600'
    );

    if (childWindow) {
      setOpenWindows(prev => new Set(prev).add(childWindow));
      setOpenSystemIds(prev => new Set(prev).add(systemId));

      const checkWindow = setInterval(() => {
        if (childWindow.closed) {
          clearInterval(checkWindow);
          setOpenWindows(prev => {
            const newSet = new Set(prev);
            newSet.delete(childWindow);
            return newSet;
          });
          setOpenSystemIds(prev => {
            const newSet = new Set(prev);
            newSet.delete(systemId);
            return newSet;
          });
        }
      }, 500);
    }
  };

  const isActionDisabled = (systemId) => openSystemIds.size > 0;

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                システム番号
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                システム名
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                状態
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                アクション
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {systemData.map(system => (
              <tr key={system.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {system.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {system.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {openSystemIds.has(system.id) ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      編集中
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      待機中
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="flex space-x-2">
                    <button
                      className={`inline-flex items-center px-2 py-1 border rounded-md 
                        ${isActionDisabled(system.id)
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-blue-50 text-blue-600 hover:bg-blue-100 border-blue-200'}`}
                      onClick={() => !isActionDisabled(system.id) && openChildWindow(system.id, 'view')}
                      disabled={isActionDisabled(system.id)}
                      title="参照"
                    >
                      <Eye className="w-4 h-4" />
                      <span className="ml-1">参照</span>
                    </button>
                    <button
                      className={`inline-flex items-center px-2 py-1 border rounded-md
                        ${isActionDisabled(system.id)
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-green-50 text-green-600 hover:bg-green-100 border-green-200'}`}
                      onClick={() => !isActionDisabled(system.id) && openChildWindow(system.id, 'edit')}
                      disabled={isActionDisabled(system.id)}
                      title="更新"
                    >
                      <Edit2 className="w-4 h-4" />
                      <span className="ml-1">更新</span>
                    </button>
                    <button
                      className={`inline-flex items-center px-2 py-1 border rounded-md
                        ${isActionDisabled(system.id)
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-purple-50 text-purple-600 hover:bg-purple-100 border-purple-200'}`}
                      onClick={() => !isActionDisabled(system.id) && openChildWindow(system.id, 'copy')}
                      disabled={isActionDisabled(system.id)}
                      title="コピー登録"
                    >
                      <Copy className="w-4 h-4" />
                      <span className="ml-1">コピー</span>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SystemTable;

```

このデザインの主なポイントは：

1. **視覚的な整理**:
   - アイコンとテキストの組み合わせで直感的な操作性を実現
   - ボタンごとに異なる色を使用して区別しつつ、トーンを抑えた配色で統一感を維持
   - ホバー効果でインタラクティブ性を向上

2. **スペースの効率的な使用**:
   - コンパクトなボタンデザインで横並びに配置
   - 適切な余白設定で視認性を確保

3. **状態の明確な表示**:
   - 編集中/待機中の状態をバッジで視覚的に表示
   - 非活性状態を明確に区別

4. **アクセシビリティ**:
   - ボタンにツールチップを追加
   - キーボード操作に対応
   - アイコンと文字の併用で理解しやすい設計

改善のためのオプション：

1. **レスポンシブ対応の強化**:
   - 画面幅に応じてボタンをドロップダウンに変更
   - モバイル表示時の最適化

2. **アニメーション追加**:
   - ボタンのホバー時のスムーズな遷移
   - 状態変更時のアニメーション

3. **カスタマイズ機能**:
   - ユーザーごとによく使う機能の並び順変更
   - ショートカットキーの設定

これらの改善を加えることで、さらに使いやすいUIにすることができます。どの方向での改善が望ましいでしょうか？
