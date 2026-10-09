選択された画面（Master-Detail / スライドオーバードロワー方式のデータグリッド）を他の生成AIやコーディング支援AI（Claude, ChatGPT, v0, Cursorなど）に依頼する際にそのまま使える**「指示プロンプト」と、コピペですぐ動かせる「React + Tailwind CSSの実装コード」**をまとめました。
1. 他のAIにそのまま渡せるプロンプト（推奨）

以下をそのままAIチャット（v0、ChatGPT、Claudeなど）に貼り付けて送信してください。

# 依頼：React + Tailwind CSS による「マスタ・詳細（ドロワー方式）」管理画面の作成

BtoB SaaSや業務管理システムでよく使われる「データグリッド一覧 ＋ 右側スライドオーバードロワー詳細」の画面コンポーネントを作成してください。

## 1. 画面構成（Master-Detail Pattern / Slide-over Drawer）
- **左側（マスタ領域 / 背景）**:
  - ヘッダー（タイトル、検索バー、ステータス絞り込み、エクスポートボタン、新規登録ボタン）
  - KPIサマリーカード（有効契約数、月次MRR、更新予定件数など）
  - データグリッド（テーブル）：チェックボックス、ID、プラン名、顧客企業名、金額、ステータスバッジ
  - 行をクリックすると、そのレコードが選択状態（ハイライト）になり、右側の詳細ドロワーが開くこと。
- **右側（詳細ドロワー / サイドシート）**:
  - 一覧の上に右端から幅 480px〜560px 程度でオーバーレイ表示（またはスライドイン）。
  - ヘッダー：ステータスバッジ、レコードID、タイトル、全画面展開アイコン、閉じる（✕）ボタン。
  - 主要アクションボタン：
    1. **「このレコードを複製して新規作成」**（目立つPrimary/Secondaryボタンスタイル）
    2. 「編集」ボタン、およびアクションメニュー（...）
  - アラート/ヒント：「ワンクリック複製機能：クリックするとIDや作成日を除外した設定内容を新規登録フォームに引き継いで遷移します」
  - タブ切り替え（基本情報 / 契約条件・金額 / 履歴・ログ）
  - レコード詳細情報（顧客・担当アカウント情報、契約金額・内訳、フッターの印刷・閉じるボタン等）

## 2. 重要な仕様・機能要件
1. **Reactステート管理**:
   - `selectedRecord`: 選択中のレコード（nullの場合はドロワー非表示、値があればドロワー表示）。
   - 行をクリックすると `setSelectedRecord(record)` でドロワーオープン。
   - 閉じるボタンまたはオーバーレイ背景クリックで `setSelectedRecord(null)`。
2. **「複製して新規作成」のアクション**:
   - クリック時、元レコードの `id` や作成日を除外し、タイトルに `(コピー)` を付加したデータをログ出力または遷移（`navigate('/contracts/new', { state: { initialData } })`）するハンドラーを用意すること。
3. **デザイン・スタイリング**:
   - Tailwind CSS を使用し、モダンな業務ダッシュボード（クリーン、視認性の高いテーブル、洗練された影と境界線）に仕上げてください。
   - アイコンには `lucide-react` を使用してください。

2. そのまま動かせるReact実装コード（TypeScript + Tailwind CSS + Lucide Icons）

import React, { useState } from 'react';
import { 
  Copy, Edit3, X, Maximize2, Search, Filter, 
  Download, Plus, ShieldCheck, Clock, TrendingUp,
  FileText, Printer, CheckSquare, Square
} from 'lucide-react';

// レコードの型定義
interface ContractRecord {
  id: string;
  planName: string;
  clientName: string;
  category: string;
  monthlyAmount: number;
  status: 'active' | 'draft' | 'pending';
  assignedUser: string;
  contractDate: string;
}

// サンプルデータ
const INITIAL_DATA: ContractRecord[] = [
  {
    id: 'CT-2024-0891',
    planName: 'エンタープライズ年額プラン (Premium)',
    clientName: '株式会社サイバーネクスト',
    category: 'クラウドSaaS',
    monthlyAmount: 1200000,
    status: 'active',
    assignedUser: '佐藤 健一 (営業1課)',
    contractDate: '2024/04/01',
  },
  {
    id: 'CT-2024-0890',
    planName: 'スタンダード月額プラン (STD)',
    clientName: 'トウキョウ・フィナンシャル',
    category: 'クラウドSaaS',
    monthlyAmount: 350000,
    status: 'active',
    assignedUser: '鈴木 花子 (営業2課)',
    contractDate: '2024/05/15',
  },
  {
    id: 'CT-2024-0889',
    planName: 'プロフェッショナル2年長期 (PRO)',
    clientName: 'オリエント・ロジスティクス',
    category: 'オンプレ保守',
    monthlyAmount: 2450000,
    status: 'active',
    assignedUser: '高橋 涼 (営業1課)',
    contractDate: '2024/01/10',
  },
];

export const MasterDetailDrawerPage: React.FC = () => {
  const [records] = useState<ContractRecord[]>(INITIAL_DATA);
  const [selectedRecord, setSelectedRecord] = useState<ContractRecord | null>(INITIAL_DATA[0]);
  const [activeTab, setActiveTab] = useState<'basic' | 'terms' | 'logs'>('basic');

  // レコード複製処理ハンドラー
  const handleDuplicate = (record: ContractRecord) => {
    // 複製時に除外または初期化すべき項目を分離
    const { id, status, ...cloneableData } = record;
    const duplicatedPayload = {
      ...cloneableData,
      planName: `${cloneableData.planName} (コピー)`,
      status: 'draft', // 下書きへリセット
    };

    console.log('新規作成画面へ引き継ぐデータ:', duplicatedPayload);
    alert(`【複製新規作成】\n${record.id} の内容を引き継いで新規作成フォームへ遷移します。\nプラン名: ${duplicatedPayload.planName}`);
    // 例: navigate('/contracts/new', { state: { initialData: duplicatedPayload } });
  };

  return (
    <div className="relative min-h-screen bg-slate-50 text-slate-800 font-sans">
      {/* メイン一覧エリア（マスタ） */}
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* 上部ヘッダー */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-xs font-semibold text-indigo-600 tracking-wider">CONSOLE / OPERATIONS</div>
            <h1 className="text-2xl font-bold text-slate-900">契約管理 / 契約プラン一覧</h1>
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium border border-slate-300 rounded-lg bg-white hover:bg-slate-50">
              <Download className="w-4 h-4 text-slate-500" />
              CSV出力
            </button>
            <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm">
              <Plus className="w-4 h-4" />
              新規契約登録
            </button>
          </div>
        </div>

        {/* KPIカード群 */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
            <div className="text-xs text-slate-500">有効契約総数</div>
            <div className="text-2xl font-bold mt-1 text-slate-900">142 <span className="text-sm font-normal text-slate-500">社</span></div>
          </div>
          <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
            <div className="text-xs text-slate-500">月次契約MRR</div>
            <div className="text-2xl font-bold mt-1 text-slate-900">¥89,450,000</div>
          </div>
          <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
            <div className="text-xs text-slate-500">今月末更新予定</div>
            <div className="text-2xl font-bold mt-1 text-slate-900">18 <span className="text-sm font-normal text-slate-500">件</span></div>
          </div>
          <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-xs">
            <div className="text-xs text-slate-500">平均更新率 (LTV)</div>
            <div className="text-2xl font-bold mt-1 text-slate-900">98.2%</div>
          </div>
        </div>

        {/* テーブルコンテナ */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input 
                type="text" 
                placeholder="契約コード、企業名で検索..." 
                className="w-full pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              />
            </div>
            <button className="flex items-center gap-1.5 px-3 py-2 text-sm border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-600">
              <Filter className="w-4 h-4" /> 絞り込み
            </button>
          </div>

          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50/75 border-b border-slate-200 text-xs font-semibold text-slate-500">
              <tr>
                <th className="py-3 px-4 w-10">#</th>
                <th className="py-3 px-4">契約コード</th>
                <th className="py-3 px-4">契約プラン名</th>
                <th className="py-3 px-4">顧客企業名</th>
                <th className="py-3 px-4">月額費用</th>
                <th className="py-3 px-4">ステータス</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {records.map((record) => {
                const isSelected = selectedRecord?.id === record.id;
                return (
                  <tr 
                    key={record.id}
                    onClick={() => setSelectedRecord(record)}
                    className={`cursor-pointer transition-colors ${
                      isSelected 
                        ? 'bg-indigo-50/70 border-l-4 border-l-indigo-600' 
                        : 'hover:bg-slate-50/80'
                    }`}
                  >
                    <td className="py-3.5 px-4 text-slate-400">
                      {isSelected ? <CheckSquare className="w-4 h-4 text-indigo-600" /> : <Square className="w-4 h-4" />}
                    </td>
                    <td className="py-3.5 px-4 font-mono font-medium text-indigo-600">{record.id}</td>
                    <td className="py-3.5 px-4 font-medium text-slate-900">{record.planName}</td>
                    <td className="py-3.5 px-4 text-slate-600">{record.clientName}</td>
                    <td className="py-3.5 px-4 font-medium text-slate-900">¥{record.monthlyAmount.toLocaleString()}</td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                        有効 (Active)
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 右側スライドオーバードロワー（詳細） */}
      {selectedRecord && (
        <div className="fixed inset-y-0 right-0 z-40 w-full max-w-xl bg-white shadow-2xl border-l border-slate-200 flex flex-col transform transition-transform duration-300 ease-in-out">
          {/* ドロワーヘッダー */}
          <div className="p-5 border-b border-slate-200 flex items-start justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                  有効 (Active)
                </span>
                <span className="text-xs text-slate-400 font-mono">REVISION #14</span>
              </div>
              <h2 className="text-lg font-bold text-slate-900">契約詳細: {selectedRecord.id}</h2>
              <p className="text-xs text-indigo-600 font-medium">{selectedRecord.planName}</p>
            </div>
            <div className="flex items-center gap-1 text-slate-400">
              <button className="p-1.5 hover:text-slate-600 hover:bg-slate-100 rounded-lg">
                <Maximize2 className="w-4 h-4" />
              </button>
              <button 
                onClick={() => setSelectedRecord(null)}
                className="p-1.5 hover:text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* ドロワーメインアクション */}
          <div className="p-5 border-b border-slate-100 bg-slate-50/50 space-y-3">
            <div className="flex items-center gap-2">
              {/* コア機能：複製ボタン */}
              <button 
                onClick={() => handleDuplicate(selectedRecord)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg shadow-sm transition-all"
              >
                <Copy className="w-4 h-4" />
                このレコードを複製して新規作成
              </button>
              <button className="flex items-center gap-1.5 px-4 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-lg">
                <Edit3 className="w-4 h-4" />
                編集
              </button>
            </div>

            {/* ガイドバナー */}
            <div className="p-3 bg-indigo-50/60 border border-indigo-100 rounded-lg text-xs text-indigo-900 leading-relaxed">
              💡 <strong>ワンクリック複製機能</strong>: クリックすると、IDや作成日を除外した設定内容を新規登録フォームに引き継いで遷移します。
            </div>
          </div>

          {/* タブナビゲーション */}
          <div className="flex border-b border-slate-200 px-5 text-sm font-medium text-slate-500">
            <button 
              onClick={() => setActiveTab('basic')}
              className={`py-3 px-2 border-b-2 transition-colors ${activeTab === 'basic' ? 'border-indigo-600 text-indigo-600 font-semibold' : 'border-transparent hover:text-slate-800'}`}
            >
              基本情報
            </button>
            <button 
              onClick={() => setActiveTab('terms')}
              className={`py-3 px-2 border-b-2 transition-colors ${activeTab === 'terms' ? 'border-indigo-600 text-indigo-600 font-semibold' : 'border-transparent hover:text-slate-800'}`}
            >
              契約条件・金額
            </button>
            <button 
              onClick={() => setActiveTab('logs')}
              className={`py-3 px-2 border-b-2 transition-colors ${activeTab === 'logs' ? 'border-indigo-600 text-indigo-600 font-semibold' : 'border-transparent hover:text-slate-800'}`}
            >
              履歴・ログ <span className="ml-1 text-xs px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-600">14</span>
            </button>
          </div>

          {/* ドロワーコンテンツ本体 */}
          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">顧客・担当アカウント情報</h3>
              <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-100 text-xs">
                <div>
                  <span className="text-slate-400 block mb-1">契約コード</span>
                  <span className="font-mono font-semibold text-slate-800">{selectedRecord.id}</span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-1">顧客企業</span>
                  <span className="font-semibold text-slate-800">{selectedRecord.clientName}</span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-1">社内担当者</span>
                  <span className="text-slate-800">{selectedRecord.assignedUser}</span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-1">契約締結日</span>
                  <span className="text-slate-800">{selectedRecord.contractDate}</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">契約金額・月額料金明細</h3>
              <div className="p-4 bg-white border border-slate-200 rounded-xl space-y-2">
                <div className="flex justify-between items-baseline">
                  <span className="text-xs text-slate-500">月額基本料 (税込)</span>
                  <span className="text-xl font-bold text-slate-900">¥{selectedRecord.monthlyAmount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-baseline pt-2 border-t border-slate-100">
                  <span className="text-xs text-slate-500">年換算バリュー (ACV)</span>
                  <span className="text-sm font-semibold text-slate-700">¥{(selectedRecord.monthlyAmount * 12).toLocaleString()} /年</span>
                </div>
              </div>
            </div>
          </div>

          {/* ドロワーフッター */}
          <div className="p-4 border-t border-slate-200 bg-white flex items-center justify-between">
            <button className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg">
              <Printer className="w-3.5 h-3.5" /> 印刷 / PDF
            </button>
            <button 
              onClick={() => setSelectedRecord(null)}
              className="px-4 py-2 text-xs font-medium border border-slate-200 hover:bg-slate-50 rounded-lg"
            >
              閉じる
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

プロンプト活用のコツ

    Tailwind以外のUIライブラリを使う場合: プロンプト内の Tailwind CSS の部分を shadcn/ui (Sheetコンポーネント) や MUI (Drawer)、Ant Design (Drawer) に書き換えると、指定したライブラリに沿ったコードが出力されます。
    フォーム遷移のライブラリを指定したい場合: 「React Router v6 の useNavigate と location.state を使用して遷移コードを書いてください」と一行追加するとより具体的になります。
