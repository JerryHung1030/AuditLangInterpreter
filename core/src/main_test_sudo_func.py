from semantic_tree_executor import SSHManager, ExecutionNodeExecutor

def main():
    # 設定 SSH 連線資訊
    hostname = "192.168.70.150"
    username = "jerryhung"
    password = "systemadmin!23"
    
    # 初始化 SemanticTreeExecutor 和 SSHManager
    ssh_manager = SSHManager(hostname, username, password)
    
    # 測試連線
    try:
        ssh_manager.connect()
        print("SSH 連線成功")
    except Exception as e:
        print(f"SSH 連線失敗: {str(e)}")
        return
    
    # 測試 check_file_existence
    executor = ExecutionNodeExecutor(
        node_type='f', 
        main_target='/etc/hosts', 
        sub_target=None, 
        target_pattern=None, 
        os_type='linux'
    )
    result = executor.check_file_existence(ssh_manager)
    print(f"檢查檔案存在: {result.to_dict()}")

    # 測試 check_directory_existence
    executor = ExecutionNodeExecutor(
        node_type='d', 
        main_target='/var/log', 
        sub_target=None, 
        target_pattern=None, 
        os_type='linux'
    )
    result = executor.check_directory_existence(ssh_manager)
    print(f"檢查目錄存在: {result.to_dict()}")

    # 測試 list_files_with_pattern
    executor = ExecutionNodeExecutor(
        node_type='d', 
        main_target='/var/log', 
        sub_target=None, 
        target_pattern='.*log', 
        os_type='linux'
    )
    result = executor.list_files_with_pattern(ssh_manager)
    print(f"列出符合條件的檔案: {result.to_dict()}")

    # 測試 run_command
    executor = ExecutionNodeExecutor(
        node_type='c', 
        main_target='ls -l', 
        sub_target=None, 
        target_pattern=None, 
        os_type='linux'
    )
    result = executor.run_command(ssh_manager)
    print(f"執行命令結果: {result.to_dict()}")

    # 測試 check_process_existence
    executor = ExecutionNodeExecutor(
        node_type='p', 
        main_target='sshd', 
        sub_target=None, 
        target_pattern=None, 
        os_type='linux'
    )
    result = executor.check_process_existence(ssh_manager)
    print(f"檢查進程存在: {result.to_dict()}")

    # 測試 determine_actual_os_type
    try:
        os_type = executor.determine_actual_os_type(ssh_manager)
        print(f"實際系統類型: {os_type}")
    except Exception as e:
        print(f"檢測 OS 類型失敗: {str(e)}")
    
    # 測試 check_registry_key (如果是 Windows)
    # 可選測試項目：在 Linux 系統上無法進行
    # executor = ExecutionNodeExecutor(
    #     node_type='r', 
    #     main_target='HKLM\\Software\\Microsoft', 
    #     sub_target='Windows', 
    #     target_pattern=None, 
    #     os_type='windows'
    # )
    # result = executor.check_registry_key(ssh_manager)
    # print(f"檢查註冊表鍵存在: {result.to_dict()}")
    
    # 關閉 SSH 連線
    ssh_manager.close()

if __name__ == "__main__":
    main()