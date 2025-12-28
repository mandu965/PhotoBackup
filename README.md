````md
# Photo Backup (MVP)

Windows 환경에서 iPhone/Android(갤럭시) 기기를 USB로 연결해 사진/영상 파일을 외장하드로 백업하는 **MVP** 프로그램입니다.

- iPhone의 **HEIC → JPG 변환** 지원
- 촬영일(가능 시 메타데이터) 기준 **YYYY/MM 폴더 분류**
- **중복 파일 스킵**
- 실행 로그 저장

---

## 설치

```text
pip install -r requirements.txt
````

---

## 기본 실행

```text
python main.py --source "D:\\ai\\photoBackup\\test_origin" --target "D:\\ai\\photoBackup\\test_copy"
```

> 팁: Windows 탐색기에서 경로를 복사해 그대로 붙여넣으면 안전합니다.

---

## 설정 파일 사용 (선택)

* `.env` 또는 `config.json` 으로 기본 경로를 저장할 수 있습니다.
* 우선순위: **CLI args > config 파일 > .env**

### 예시 `.env`

```text
SOURCE_DIR=D:\\DCIM
TARGET_DIR=E:\\PHOTO_BACKUP
```

### 예시 `config.json`

> 주의: Windows 경로는 `\\`(백슬래시 2개)로 작성하는 것을 권장합니다.

```json
{
  "SOURCE_DIR": "D:\\\\DCIM",
  "TARGET_DIR": "E:\\\\PHOTO_BACKUP"
}
```

---

## 옵션

```text
--source                 복사 대상 디렉토리(휴대폰 DCIM 등)
--target                 백업 대상 루트 디렉토리(외장하드 등)
--config                 설정 파일 경로(.env 또는 config.json)
--dry-run                실제 복사/변환 없이 계획만 출력/로그
--hash                   SHA-256 해시 기반 중복 검사 활성화
--copy-heic-on-fail       HEIC 변환 실패 시 원본 HEIC 복사(기본: 스킵)
--workers N              워커 수(현재 MVP는 1로 동작)
--extensions             확장자 목록 재정의(예: .jpg,.jpeg,.png,.heic,.mp4,.mov)
```

---

## Docker (선택)

### docker build/run

```text
docker build -t photo-backup .

docker run --rm ^
  -v "D:/DCIM:/data/source:ro" ^
  -v "E:/PHOTO_BACKUP:/data/target" ^
  -v "%cd%/logs:/app/logs" ^
  -e SOURCE_DIR=/data/source ^
  -e TARGET_DIR=/data/target ^
  photo-backup
```

### docker compose

```text
docker compose up --build
백그라운드
docker compose up -d
로그확인
docker compose logs -f

```

### 실행
docker compose run --rm photo-backup python main.py
docker compose run --rm -e SOURCE_DIR=/data/source -e TARGET_DIR=/data/target photo-backup python main.py



> `docker-compose.yml` 은 환경에 맞게 볼륨 경로를 조정하세요.

---

## Windows에서 경로 잡는 법

* iPhone/Android를 USB로 연결하면 보통 **탐색기에서 DCIM 폴더**가 보입니다.
* 해당 폴더의 경로를 복사해 `--source` 에 넣으세요.
* 백업 위치는 외장하드 루트(예: `E:\\PHOTO_BACKUP`)를 `--target` 으로 지정합니다.

---

## 메타데이터 처리 방식(중요)

* 이미지(HEIC/JPG/PNG)는 가능한 경우 **EXIF의 DateTimeOriginal** 등을 우선 사용합니다.
* 영상(MP4/MOV)은 환경/라이브러리 제약으로 촬영일 추출이 어려울 수 있어, 기본값으로 **파일 수정일(mtime)** 을 사용합니다.

  * TODO(확장): `ffprobe` 또는 `MediaInfo` 를 연동해 영상 촬영일을 더 정확히 추출

---

## 로그

실행 로그는 아래 형태로 저장됩니다.

```text
logs/backup_YYYY-MM-DD.log
```

---
