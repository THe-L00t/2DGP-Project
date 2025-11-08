from PIL import Image
import os

def analyze_image(image_path):
    """
    이미지의 유효한 픽셀 범위를 분석 (알파 채널 > 0인 영역)
    pico2d 좌표계: 왼쪽 하단이 (0, 0)
    """
    img = Image.open(image_path)

    # RGBA 모드로 변환
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    width, height = img.size
    pixels = img.load()

    # 유효한 픽셀 찾기
    min_x = width
    max_x = 0
    min_y = height
    max_y = 0

    has_valid_pixel = False

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # 알파 채널이 0보다 크면 유효한 픽셀
            if a > 0:
                has_valid_pixel = True
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

    if not has_valid_pixel:
        return None

    # PIL 좌표계 (위쪽이 0) -> pico2d 좌표계 (아래쪽이 0)로 변환
    # PIL: y=0 (위) ~ y=height (아래)
    # pico2d: y=0 (아래) ~ y=height (위)
    pico2d_min_y = height - max_y - 1
    pico2d_max_y = height - min_y - 1

    return {
        'width': width,
        'height': height,
        'bbox_min_x': min_x,
        'bbox_max_x': max_x,
        'bbox_min_y': pico2d_min_y,
        'bbox_max_y': pico2d_max_y,
        'bbox_width': max_x - min_x + 1,
        'bbox_height': max_y - min_y + 1
    }

def main():
    resource_dir = 'resource'

    # Warrior와 Child를 제외한 파일들 (배경 타일)
    exclude_keywords = ['Warrior', 'Child']

    results = []

    # resource 폴더의 모든 png 파일 분석
    for filename in os.listdir(resource_dir):
        if not filename.endswith('.png'):
            continue

        # Warrior, Child 제외
        if any(keyword in filename for keyword in exclude_keywords):
            continue

        filepath = os.path.join(resource_dir, filename)

        print(f"Analyzing: {filename}")
        result = analyze_image(filepath)

        if result:
            results.append({
                'filename': filename,
                'data': result
            })

    # 결과를 텍스트 파일로 저장
    output_path = os.path.join(resource_dir, 'tile_bounds.txt')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("타일 이미지 유효 픽셀 범위 분석 결과\n")
        f.write("좌표계: pico2d (왼쪽 하단이 원점)\n")
        f.write("=" * 80 + "\n\n")

        for item in results:
            filename = item['filename']
            data = item['data']

            f.write(f"파일명: {filename}\n")
            f.write(f"  이미지 크기: {data['width']}x{data['height']}\n")
            f.write(f"  유효 영역 (pico2d 좌표):\n")
            f.write(f"    X 범위: {data['bbox_min_x']} ~ {data['bbox_max_x']} (너비: {data['bbox_width']})\n")
            f.write(f"    Y 범위: {data['bbox_min_y']} ~ {data['bbox_max_y']} (높이: {data['bbox_height']})\n")
            f.write(f"  바운딩 박스 (left, bottom, right, top):\n")
            f.write(f"    ({data['bbox_min_x']}, {data['bbox_min_y']}, {data['bbox_max_x']}, {data['bbox_max_y']})\n")
            f.write("\n" + "-" * 80 + "\n\n")

    print(f"\n분석 완료! 결과 저장: {output_path}")
    print(f"총 {len(results)}개 타일 이미지 분석됨")

if __name__ == '__main__':
    main()
