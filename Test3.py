import time
import pandas as pd
from openpyxl import load_workbook
import paramiko
import scp
import argparse

def upload_file(hostname, username, password, port, local_path, remote_path):
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password,port=port)

        # SCP上传文件到远程服务器
        with scp.SCPClient(ssh.get_transport()) as scp_client:
            scp_client.put(local_path, remote_path)

        # 添加权限并执行，将输出保存到文件
        #command = f"chmod +x {remote_path} && {remote_path} > /tmp/out1.txt 2>&1"
        print(remote_path)
        print(f"给脚本添加权限----------{hostname}")
        command = f"chmod +x {remote_path}"
        stdin, stdout, stderr = ssh.exec_command(command)

        # 检查是否有错误信息
        err = stderr.read().decode()
        if err != '':
            raise Exception(f"执行： {hostname} failed:\n{err}")

        # invoke = ssh.invoke_shell()
        # invoke.send("/tmp/linux_baseline_level3.sh")
        # time.sleep(30)  # 等待命令执行完毕
        print(f"权限添加完毕----------{hostname}")
        print(f"运行基线脚本----------{hostname}")
        stdin2, stdout2, stderr2 = ssh.exec_command(f"cd /tmp && /tmp/{local_path} &")  # 执行命令并获取命令结果
        # stdin为输入的命令
        # stdout为命令返回的结果
        # stderr为命令错误时返回的结果
        res, err = stdout2.read(), stderr2.read()
        result = res if res else err
        print(result.decode().strip())


        # 下载输出文件
        with scp.SCPClient(ssh.get_transport()) as scp_client:
            scp_client.get('/tmp/out.txt', f"{hostname}_out.txt")


        #清楚遗留文件
        print(f"清除遗留文件----------{hostname}")
        stdin2, stdout2, stderr2 = ssh.exec_command(f"rm -rf  /tmp/{local_path} /tmp/out.txt")  # 执行命令并获取命令结果
        # stdin为输入的命令
        # stdout为命令返回的结果
        # stderr为命令错误时返回的结果
        res, err = stdout2.read(), stderr2.read()
        result = res if res else err
        print(f"清除完毕----------{hostname}")



def main():
    # 创建解析器并添加-f选项
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='请指定当前目录下的sh脚本')

    # 解析命令行参数
    args = parser.parse_args()

    # 获取指定的文件名
    filenamesh = args.file

    # 读取Excel文件
    wb = load_workbook(filename='target.xlsx')
    ws = wb.active

    # 将Excel数据转换为DataFrame
    df = pd.DataFrame(ws.values)
    df.columns = ['host', 'username', 'password', 'port']

    #
    #filenamesh = 'linux_baseline_level3.sh'
    local_file_path = filenamesh
    remote_file_path = '/tmp/' + filenamesh


    # 遍历每一行，上传文件并执行远程脚本，下载输出文件
    for index, row in df.iloc[1:].iterrows():
        hostname = row['host']
        username = row['username']
        password = str(row['password'])
        port = str(row['port'])
        #print(hostname, username, password, port)
        #print(type(hostname), type(username), type(password), type(port))

        try:
            upload_file(hostname, username, password, port, local_file_path, remote_file_path)
            print(f"执行完毕： {hostname} succeeded!")
        except Exception as e:
            print(e)
        print("\n")

if __name__ == '__main__':
    main()