from io import BytesIO
from pathlib import Path
from rembg import remove
from PIL import Image
from flask import Flask, request, jsonify
import os
import boto3

# 直接指定存储桶名称
BUCKET_NAME = 'hhw-background-remove'  # 请将此处替换为您实际的存储桶名称

# 初始化 S3 客户端
s3_client = boto3.client('s3', endpoint_url='http://localhost:9000',
                         aws_access_key_id='S3RVER',
                         aws_secret_access_key='S3RVER')

app = Flask(__name__)

def process_image(key):
    try:
        print(f"开始处理图像: {key}")
        
        # 从S3读取图片
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
        image_data = response['Body'].read()

        # 去除背景
        output = remove(image_data)

        # 生成新的文件名
        new_key = f'no_bg_{key}'

        # 将处理后的图像保存到S3
        s3_client.put_object(Body=output, Bucket=BUCKET_NAME, Key=new_key)
        print(f"处理后的图像已保存到S3: {new_key}")

        # 保存处理后的图像到本地（用于调试）
        # 确保文件名有正确的扩展名
        _, file_extension = os.path.splitext(key)
        if not file_extension:
            file_extension = '.png'  # 默认使用 PNG 格式
        output_path = f"./processed_{key}{file_extension}"
        
        # 使用 PIL 来保存图像
        img = Image.open(BytesIO(output))
        img.save(output_path)
        print(f"处理后的图像已保存至本地: {output_path}")

        return new_key
    except Exception as e:
        print(f"处理图像时出错: {str(e)}")
        raise

@app.route('/remove-background', methods=['POST'])
def remove_background():
    data = request.json
    try:
        print(f"使用的存储桶名称: {BUCKET_NAME}")
        new_key = process_image(data['s3Key'])
        return jsonify({"newS3Key": new_key})
    except Exception as e:
        print(f"详细错误信息: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 在启动应用之前检查并创建存储桶（如果不存在）
def ensure_bucket_exists():
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"存储桶 {BUCKET_NAME} 已存在")
    except:
        try:
            s3_client.create_bucket(Bucket=BUCKET_NAME)
            print(f"存储桶 {BUCKET_NAME} 已创建")
        except Exception as e:
            print(f"创建存储桶时出错: {str(e)}")
            raise

if __name__ == "__main__":
    ensure_bucket_exists()
    app.run(debug=True, port=5000)