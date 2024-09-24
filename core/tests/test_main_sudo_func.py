from semantic_tree_executor import SSHManager, ExecutionNodeExecutor

def main():
    # Set SSH connection information
    hostname = "192.168.70.150"
    username = "jerryhung"
    password = "systemadmin!23"
    
    # Initialize SemanticTreeExecutor and SSHManager
    ssh_manager = SSHManager(hostname, username, password)
    
    # Test connection
    try:
        ssh_manager.connect()
        print("SSH connection successful")
    except Exception as e:
        print(f"SSH connection failed: {str(e)}")
        return
    
    # Test check_file_existence
    executor = ExecutionNodeExecutor(
        node_type='f', 
        main_target='/etc/hosts', 
        sub_target=None, 
        target_pattern=None, 
        os_type='linux'
    )
    result = executor.check_file_existence(ssh_manager)
    print(f"File existence check: {result.to_dict()}")

    # Test check_directory_existence
    executor = ExecutionNodeExecutor(
        node_type='d', 
        main_target='/var/log', 
        sub_target=None, 
        target_pattern=None, 
        os_type='linux'
    )
    result = executor.check_directory_existence(ssh_manager)
    print(f"Directory existence check: {result.to_dict()}")

    # Test list_files_with_pattern
    executor = ExecutionNodeExecutor(
        node_type='d', 
        main_target='/var/log', 
        sub_target=None, 
        target_pattern='.*log', 
        os_type='linux'
    )
    result = executor.list_files_with_pattern(ssh_manager)
    print(f"List files matching pattern: {result.to_dict()}")

    # Test run_command
    executor = ExecutionNodeExecutor(
        node_type='c', 
        main_target='ls -l', 
        sub_target=None, 
        target_pattern=None, 
        os_type='linux'
    )
    result = executor.run_command(ssh_manager)
    print(f"Command execution result: {result.to_dict()}")

    # Test check_process_existence
    executor = ExecutionNodeExecutor(
        node_type='p', 
        main_target='sshd', 
        sub_target=None, 
        target_pattern=None, 
        os_type='linux'
    )
    result = executor.check_process_existence(ssh_manager)
    print(f"Process existence check: {result.to_dict()}")

    # Test determine_actual_os_type
    try:
        os_type = executor.determine_actual_os_type(ssh_manager)
        print(f"Actual OS type: {os_type}")
    except Exception as e:
        print(f"Failed to determine OS type: {str(e)}")
    
    # Test check_registry_key (if Windows)
    # Optional test: cannot run on Linux systems
    # executor = ExecutionNodeExecutor(
    #     node_type='r', 
    #     main_target='HKLM\\Software\\Microsoft', 
    #     sub_target='Windows', 
    #     target_pattern=None, 
    #     os_type='windows'
    # )
    # result = executor.check_registry_key(ssh_manager)
    # print(f"Registry key existence check: {result.to_dict()}")
    
    # Close SSH connection
    ssh_manager.close()

if __name__ == "__main__":
    main()
