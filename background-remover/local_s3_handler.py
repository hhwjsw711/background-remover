import boto3

# 初始化 S3 客户端
s3_client = boto3.client('s3', endpoint_url='http://localhost:9000',
                         aws_access_key_id='S3RVER',
                         aws_secret_access_key='S3RVER')

def list_buckets():
    response = s3_client.list_buckets()
    print("存储桶列表:")
    for bucket in response['Buckets']:
        print(f"- {bucket['Name']}")

def list_objects(bucket_name):
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    print(f"{bucket_name} 中的对象:")
    for obj in response.get('Contents', []):
        print(f"- {obj['Key']}")

def delete_bucket(bucket_name):
    try:
        # 首先删除桶中的所有对象
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        for obj in response.get('Contents', []):
            s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
        
        # 然后删除桶
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"存储桶 {bucket_name} 已成功删除")
    except Exception as e:
        print(f"删除存储桶时出错: {e}")

def download_object(bucket_name, object_key, local_path):
    try:
        s3_client.download_file(bucket_name, object_key, local_path)
        print(f"文件 {object_key} 已成功下载到 {local_path}")
    except Exception as e:
        print(f"下载文件时出错: {e}")

if __name__ == "__main__":
    list_buckets()
    
    bucket_name = input("请输入要操作的存储桶名称: ")
    
    action = input("请选择操作 (list/delete/download): ")
    if action == 'list':
        list_objects(bucket_name)
    elif action == 'delete':
        delete_bucket(bucket_name)
    elif action == 'download':
        object_key = input("请输入要下载的文件名: ")
        local_path = input("请输入保存文件的本地路径: ")
        download_object(bucket_name, object_key, local_path)
    else:
        print("无效的操作")