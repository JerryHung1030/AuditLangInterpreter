import React, { useState } from 'react';

const ScriptManagement = () => {
  const [script, setScript] = useState('');

  const handleInputChange = (event) => {
    setScript(event.target.value);
  };

  const handleAddScript = () => {
    // 在這裡處理添加腳本的邏輯
    console.log('添加腳本:', script);
    setScript('');
  };

  return (
    <div className="dark:bg-gray-900 dark:text-white p-6 rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold mb-6">腳本管理</h1>

      <div className="relative mb-4 flex flex-wrap items-stretch">
        <span
          className="flex items-center whitespace-nowrap rounded-s border border-e-0 border-solid border-neutral-200 px-3 py-[0.25rem] text-center text-base font-normal leading-[1.6] text-surface dark:border-white/10 dark:text-white"
          id="basic-addon1"
        >@</span>
        <input
          type="text"
          className="relative m-0 block flex-auto rounded-e border border-solid border-neutral-200 bg-transparent bg-clip-padding px-3 py-[0.25rem] text-base font-normal leading-[1.6] text-surface outline-none transition duration-200 ease-in-out placeholder:text-neutral-500 focus:z-[3] focus:border-primary focus:shadow-inset focus:outline-none motion-reduce:transition-none dark:border-white/10 dark:text-white dark:placeholder:text-neutral-200 dark:autofill:shadow-autofill dark:focus:border-primary"
          placeholder="Username"
          aria-label="Username"
          aria-describedby="basic-addon1"
        />
      </div>

      <div className="relative mb-4 flex w-full flex-wrap items-stretch">
        <input
          type="text"
          className="relative m-0 block flex-auto rounded-s border border-solid border-neutral-200 bg-transparent bg-clip-padding px-3 py-[0.25rem] text-base font-normal leading-[1.6] text-surface outline-none transition duration-200 ease-in-out placeholder:text-neutral-500 focus:z-[3] focus:border-primary focus:shadow-inset focus:outline-none motion-reduce:transition-none dark:border-white/10 dark:text-white dark:placeholder:text-neutral-200 dark:autofill:shadow-autofill dark:focus:border-primary"
          placeholder="Recipient's username"
          aria-label="Recipient's username"
          aria-describedby="basic-addon2"
        />
        <span
          className="flex items-center whitespace-nowrap rounded-e border border-s-0 border-solid border-neutral-200 px-3 py-[0.25rem] text-center text-base font-normal leading-[1.6] text-surface dark:border-white/10 dark:text-white"
          id="basic-addon2"
        >@example.com</span>
      </div>

      <label
        htmlFor="basic-url"
        className="mb-2 inline-block text-surface dark:text-white"
      >Your vanity URL</label>
      <div className="relative mb-4 flex w-full flex-wrap items-stretch">
        <span
          className="flex items-center whitespace-nowrap rounded-s border border-e-0 border-solid border-neutral-200 px-3 py-[0.25rem] text-center text-base font-normal leading-[1.6] text-surface dark:border-white/10 dark:text-white"
          id="basic-addon3"
        >https://example.com/users/</span>
        <input
          type="text"
          className="relative m-0 block flex-auto rounded-e border border-solid border-neutral-200 bg-transparent bg-clip-padding px-3 py-[0.25rem] text-base font-normal leading-[1.6] text-surface outline-none transition duration-200 ease-in-out placeholder:text-neutral-500 focus:z-[3] focus:border-primary focus:shadow-inset focus:outline-none motion-reduce:transition-none dark:border-white/10 dark:text-white dark:placeholder:text-neutral-200 dark:autofill:shadow-autofill dark:focus:border-primary"
          id="basic-url"
          aria-describedby="basic-addon3"
        />
      </div>

      <div className="relative mb-4 flex w-full flex-wrap items-stretch">
        <span
          className="flex items-center whitespace-nowrap rounded-s border border-e-0 border-solid border-neutral-200 px-3 py-[0.25rem] text-center text-base font-normal leading-[1.6] text-surface dark:border-white/10 dark:text-white"
        >$</span>
        <input
          type="text"
          className="relative m-0 block flex-auto border border-solid border-neutral-200 bg-transparent bg-clip-padding px-3 py-[0.25rem] text-base font-normal leading-[1.6] text-surface outline-none transition duration-200 ease-in-out placeholder:text-neutral-500 focus:z-[3] focus:border-primary focus:shadow-inset focus:outline-none motion-reduce:transition-none dark:border-white/10 dark:text-white dark:placeholder:text-neutral-200 dark:autofill:shadow-autofill dark:focus:border-primary"
          aria-label="Amount (to the nearest dollar)"
        />
        <span
          className="flex items-center whitespace-nowrap rounded-e border border-s-0 border-solid border-neutral-200 px-3 py-[0.25rem] text-center text-base font-normal leading-[1.6] text-surface dark:border-white/10 dark:text-white"
        >.00</span>
      </div>

      <div className="relative mb-4 flex w-full flex-wrap items-stretch">
        <input
          type="text"
          className="relative m-0 block flex-auto rounded-s border border-solid border-neutral-200 bg-transparent bg-clip-padding px-3 py-[0.25rem] text-base font-normal leading-[1.6] text-surface outline-none transition duration-200 ease-in-out placeholder:text-neutral-500 focus:z-[3] focus:border-primary focus:shadow-inset focus:outline-none motion-reduce:transition-none dark:border-white/10 dark:text-white dark:placeholder:text-neutral-200 dark:autofill:shadow-autofill dark:focus:border-primary"
          placeholder="Username"
          aria-label="Username"
        />
        <span
          className="flex items-center whitespace-nowrap border border-x-0 border-solid border-neutral-200 px-3 py-[0.25rem] text-center text-base font-normal leading-[1.6] text-surface dark:border-white/10 dark:text-white"
        >@</span>
        <input
          type="text"
          className="relative m-0 block flex-auto rounded-e border border-solid border-neutral-200 bg-transparent bg-clip-padding px-3 py-[0.25rem] text-base font-normal leading-[1.6] text-surface outline-none transition duration-200 ease-in-out placeholder:text-neutral-500 focus:z-[3] focus:border-primary focus:shadow-inset focus:outline-none motion-reduce:transition-none dark:border-white/10 dark:text-white dark:placeholder:text-neutral-200 dark:autofill:shadow-autofill dark:focus:border-primary"
          placeholder="Server"
          aria-label="Server"
        />
      </div>

      <div className="relative flex w-full flex-wrap items-stretch">
        <span
          className="flex items-center whitespace-nowrap border border-e-0 border-solid border-neutral-200 px-3 py-[0.25rem] text-center text-base font-normal leading-[1.6] text-surface dark:border-white/10 dark:text-white"
        >With textarea</span>
        <textarea
          className="relative m-0 block flex-auto rounded-e border border-solid border-neutral-200 bg-transparent bg-clip-padding px-3 py-[0.25rem] text-base font-normal leading-[1.6] text-surface outline-none transition duration-200 ease-in-out placeholder:text-neutral-500 focus:z-[3] focus:border-primary focus:shadow-inset focus:outline-none motion-reduce:transition-none dark:border-white/10 dark:text-white dark:placeholder:text-neutral-200 dark:autofill:shadow-autofill dark:focus:border-primary"
          aria-label="With textarea"
        ></textarea>
      </div>
    </div>
  );
};

export default ScriptManagement;
