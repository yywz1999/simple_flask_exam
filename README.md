# simple_flask_exam
简单的考试系统/答题系统
架构：前端bootstrap+后端flask+本地sqlite存储

## 使用方法:
### python:
`python3 app.py`

### docker:
``` shell
docker build -t simple-exam-img .
docker run -p 5000:5000 simple-exam-img
```

## 效果展示
主页：
<img width="1440" alt="image" src="https://github.com/user-attachments/assets/ff357967-d9e3-41e8-877f-59d62071f8b4" />

注册&登录：
<img width="1440" alt="image" src="https://github.com/user-attachments/assets/7b8fa509-ef84-4f58-b652-28525495583c" />

导入：
<img width="1440" alt="image" src="https://github.com/user-attachments/assets/2ccd9861-52c3-42e9-a2e2-fbc18ae78f3f" />

答题（单选多选）：
![image](https://github.com/user-attachments/assets/a0972acb-a235-4ddb-8f54-9b399b72ac05)

结果：
<img width="1440" alt="image" src="https://github.com/user-attachments/assets/8bac3033-0c33-44b3-b7bc-f57fc736b9ab" />
