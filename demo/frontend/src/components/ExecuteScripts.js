import React from 'react';

const ExecuteScripts = () => {
  const handleExecuteScripts = () => {
    // 在這裡處理執行腳本的邏輯
    console.log('執行腳本');
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">執行腳本</h1>
      <button onClick={handleExecuteScripts} className="tw-element-button">
        執行所有腳本
      </button>
    </div>
  );
};

export default ExecuteScripts;
