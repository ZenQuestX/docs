SessionStorageを使用して状態を維持する実装をお見せします。



```tsx
import React, { useState, useEffect } from 'react';

const ParentWindow = () => {
  // SessionStorageから初期状態を読み込む
  const initializeOpenWindows = () => {
    const storedWindows = sessionStorage.getItem('openSystemWindows');
    return storedWindows ? new Set(JSON.parse(storedWindows)) : new Set();
  };

  const [openWindows, setOpenWindows] = useState(new Set());
  const [openSystemIds, setOpenSystemIds] = useState(initializeOpenWindows());
  const [selectedSystem, setSelectedSystem] = useState(null);

  // openSystemIdsが変更されたらSessionStorageを更新
  useEffect(() => {
    sessionStorage.setItem('openSystemWindows', JSON.stringify([...openSystemIds]));
  }, [openSystemIds]);

  // ページ読み込み時に既存の子ウィンドウをチェック
  useEffect(() => {
    const checkExistingWindows = () => {
      const systemIds = [...openSystemIds];
      systemIds.forEach(systemId => {
        const existingWindow = window.open('', `system-${systemId}`);
        if (existingWindow && !existingWindow.closed) {
          setOpenWindows(prev => new Set(prev).add(existingWindow));
        } else {
          setOpenSystemIds(prev => {
            const newSet = new Set(prev);
            newSet.delete(systemId);
            return newSet;
          });
        }
      });
    };

    checkExistingWindows();
  }, []);

  const handleContextMenu = (e, systemId) => {
    e.preventDefault();
    setSelectedSystem(systemId);
  };

  const openChildWindow = (systemId) => {
    // 既に開いているウィンドウがあれば、フォーカスを当てる
    const existingWindow = window.open('', `system-${systemId}`);
    if (existingWindow && !existingWindow.closed && openSystemIds.has(systemId)) {
      existingWindow.focus();
      return;
    }

    const childWindow = window.open(
      `/child-page/${systemId}`,
      `system-${systemId}`,
      'width=800,height=600'
    );

    if (childWindow) {
      setOpenWindows(prev => new Set(prev).add(childWindow));
      setOpenSystemIds(prev => new Set(prev).add(systemId));

      // 子ウィンドウが閉じられた時の監視
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

  // コンテキストメニューを閉じる
  const handleClickOutside = () => {
    setSelectedSystem(null);
  };

  useEffect(() => {
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  const isUpdateDisabled = openSystemIds.size > 0;

  // サンプルデータ
  const systemData = [
    { id: 1, name: "System A" },
    { id: 2, name: "System B" },
    { id: 3, name: "System C" }
  ];

  return (
    <div>
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="border p-2">システム番号</th>
            <th className="border p-2">システム名</th>
            <th className="border p-2">状態</th>
          </tr>
        </thead>
        <tbody>
          {systemData.map(system => (
            <tr key={system.id}
                onContextMenu={(e) => handleContextMenu(e, system.id)}>
              <td className="border p-2">{system.id}</td>
              <td className="border p-2">{system.name}</td>
              <td className="border p-2">
                {openSystemIds.has(system.id) ? '編集中' : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedSystem && (
        <div 
          className="absolute bg-white shadow-lg border rounded"
          style={{
            top: '100px',
            left: '100px',
            zIndex: 1000
          }}
        >
          <button
            className={`p-2 w-full text-left hover:bg-gray-100 ${
              isUpdateDisabled ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            onClick={(e) => {
              e.stopPropagation();
              if (!isUpdateDisabled) {
                openChildWindow(selectedSystem);
                setSelectedSystem(null);
              }
            }}
            disabled={isUpdateDisabled}
          >
            更新
          </button>
        </div>
      )}
    </div>
  );
};

export default ParentWindow;

```

SessionStorageを使用することで、以下のような機能が追加されました：

1. **状態の永続化**:
   - 開いているシステムのIDをSessionStorageに保存
   - ブラウザの更新後も状態を維持
   - タブを閉じるまでデータを保持

2. **ウィンドウの重複防止**:
   - 同じシステムIDのウィンドウが既に開いている場合は、そのウィンドウにフォーカスを当てる
   - 重複したウィンドウの作成を防ぐ

3. **状態の表示強化**:
   - テーブルに「状態」列を追加し、現在編集中のシステムを表示
   - ユーザーが現在どのシステムが編集中かを視覚的に確認可能

4. **エラーハンドリングの改善**:
   - ページ読み込み時に既存のウィンドウをチェック
   - 閉じられたウィンドウを適切に検知して状態を更新

このアプローチのメリット：
- ブラウザの更新後も編集状態が維持される
- ユーザーエクスペリエンスの向上（重複防止、状態表示）
- より堅牢なウィンドウ管理

必要に応じて、以下のような機能も追加できます：

1. タイムアウト処理（長時間開いているウィンドウの自動クローズ）
2. 子ウィンドウとの双方向通信（postMessage APIの使用）
3. エラー時のリカバリー処理

これらの機能も必要でしょうか？
