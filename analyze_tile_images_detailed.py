from PIL import Image
import os
import json

def analyze_frame(pixels, x_offset, width, frame_width, frame_height):
    """
    특정 프레임 영역의 유효 픽셀 분석
    """
    min_x = frame_width
    max_x = 0
    min_y = frame_height
    max_y = 0

    has_valid_pixel = False
    pixel_count = 0
    alpha_sum = 0

    for y in range(frame_height):
        for x in range(frame_width):
            px = x_offset + x
            if px >= width:
                continue

            r, g, b, a = pixels[px, y]

            if a > 0:
                has_valid_pixel = True
                pixel_count += 1
                alpha_sum += a
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

    if not has_valid_pixel:
        return None

    # pico2d 좌표계로 변환
    pico2d_min_y = frame_height - max_y - 1
    pico2d_max_y = frame_height - min_y - 1

    avg_alpha = alpha_sum / pixel_count if pixel_count > 0 else 0

    return {
        'bbox_min_x': min_x,
        'bbox_max_x': max_x,
        'bbox_min_y': pico2d_min_y,
        'bbox_max_y': pico2d_max_y,
        'bbox_width': max_x - min_x + 1,
        'bbox_height': max_y - min_y + 1,
        'pixel_count': pixel_count,
        'avg_alpha': avg_alpha
    }

def analyze_tileset(image_path, tile_size=64):
    """
    타일셋 이미지를 개별 타일로 분석
    """
    img = Image.open(image_path)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    width, height = img.size
    pixels = img.load()

    tiles_x = width // tile_size
    tiles_y = height // tile_size

    results = []

    for ty in range(tiles_y):
        for tx in range(tiles_x):
            tile_x = tx * tile_size
            tile_y = ty * tile_size

            # 타일 영역 분석
            min_x = tile_size
            max_x = 0
            min_y = tile_size
            max_y = 0

            has_valid_pixel = False
            pixel_count = 0

            for y in range(tile_size):
                for x in range(tile_size):
                    px = tile_x + x
                    py = tile_y + y

                    if px >= width or py >= height:
                        continue

                    r, g, b, a = pixels[px, py]

                    if a > 0:
                        has_valid_pixel = True
                        pixel_count += 1
                        min_x = min(min_x, x)
                        max_x = max(max_x, x)
                        min_y = min(min_y, y)
                        max_y = max(max_y, y)

            if has_valid_pixel:
                # pico2d 좌표계로 변환
                pico2d_min_y = tile_size - max_y - 1
                pico2d_max_y = tile_size - min_y - 1

                results.append({
                    'tile_index': (tx, ty),
                    'tile_pos': (tile_x, tile_y),
                    'bbox_min_x': min_x,
                    'bbox_max_x': max_x,
                    'bbox_min_y': pico2d_min_y,
                    'bbox_max_y': pico2d_max_y,
                    'bbox_width': max_x - min_x + 1,
                    'bbox_height': max_y - min_y + 1,
                    'pixel_count': pixel_count,
                    'coverage': (pixel_count / (tile_size * tile_size)) * 100
                })

    return {
        'width': width,
        'height': height,
        'tile_size': tile_size,
        'tiles_x': tiles_x,
        'tiles_y': tiles_y,
        'tiles': results
    }

def analyze_animated_tile(image_path, frame_count=12):
    """
    애니메이션 타일 이미지를 프레임별로 분석
    """
    img = Image.open(image_path)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    width, height = img.size
    pixels = img.load()

    frame_width = width // frame_count
    frame_height = height

    frames = []

    for i in range(frame_count):
        x_offset = i * frame_width
        frame_data = analyze_frame(pixels, x_offset, width, frame_width, frame_height)

        if frame_data:
            frame_data['frame_index'] = i
            frames.append(frame_data)

    return {
        'width': width,
        'height': height,
        'frame_count': frame_count,
        'frame_width': frame_width,
        'frame_height': frame_height,
        'frames': frames
    }

def analyze_single_tile(image_path):
    """
    단일 타일 이미지 분석
    """
    img = Image.open(image_path)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    width, height = img.size
    pixels = img.load()

    min_x = width
    max_x = 0
    min_y = height
    max_y = 0

    has_valid_pixel = False
    pixel_count = 0
    color_info = {}

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            if a > 0:
                has_valid_pixel = True
                pixel_count += 1
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

                # 색상 통계
                color_key = (r, g, b)
                if color_key not in color_info:
                    color_info[color_key] = 0
                color_info[color_key] += 1

    if not has_valid_pixel:
        return None

    # pico2d 좌표계로 변환
    pico2d_min_y = height - max_y - 1
    pico2d_max_y = height - min_y - 1

    # 가장 많이 사용된 색상 상위 3개
    top_colors = sorted(color_info.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        'width': width,
        'height': height,
        'bbox_min_x': min_x,
        'bbox_max_x': max_x,
        'bbox_min_y': pico2d_min_y,
        'bbox_max_y': pico2d_max_y,
        'bbox_width': max_x - min_x + 1,
        'bbox_height': max_y - min_y + 1,
        'pixel_count': pixel_count,
        'coverage': (pixel_count / (width * height)) * 100,
        'top_colors': [(f"RGB({r},{g},{b})", count) for (r,g,b), count in top_colors]
    }

def main():
    resource_dir = 'resource'
    exclude_keywords = ['Warrior', 'Child']

    results = {}

    for filename in os.listdir(resource_dir):
        if not filename.endswith('.png'):
            continue

        if any(keyword in filename for keyword in exclude_keywords):
            continue

        filepath = os.path.join(resource_dir, filename)
        print(f"Analyzing: {filename}")

        # 파일 타입에 따라 다른 분석 수행
        if 'Tilemap' in filename:
            # 타일셋 분석
            results[filename] = {
                'type': 'tileset',
                'data': analyze_tileset(filepath, tile_size=64)
            }
        elif '12frames' in filename:
            # 애니메이션 타일 분석
            results[filename] = {
                'type': 'animated',
                'data': analyze_animated_tile(filepath, frame_count=12)
            }
        else:
            # 단일 타일 분석
            results[filename] = {
                'type': 'single',
                'data': analyze_single_tile(filepath)
            }

    # 상세 결과를 텍스트 파일로 저장
    output_path = os.path.join(resource_dir, 'tile_bounds_detailed.txt')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("타일 이미지 상세 분석 결과\n")
        f.write("좌표계: pico2d (왼쪽 하단이 원점)\n")
        f.write("=" * 100 + "\n\n")

        for filename, result in sorted(results.items()):
            f.write(f"\n{'=' * 100}\n")
            f.write(f"파일명: {filename}\n")
            f.write(f"타입: {result['type']}\n")
            f.write(f"{'=' * 100}\n\n")

            data = result['data']

            if result['type'] == 'tileset':
                f.write(f"이미지 크기: {data['width']}x{data['height']}\n")
                f.write(f"타일 크기: {data['tile_size']}x{data['tile_size']}\n")
                f.write(f"타일 개수: {data['tiles_x']}x{data['tiles_y']} = {len(data['tiles'])}개 (유효 타일)\n\n")

                for tile in data['tiles']:
                    tx, ty = tile['tile_index']
                    f.write(f"  타일 [{tx}, {ty}] (위치: {tile['tile_pos']})\n")
                    f.write(f"    유효 영역: X({tile['bbox_min_x']}~{tile['bbox_max_x']}), Y({tile['bbox_min_y']}~{tile['bbox_max_y']})\n")
                    f.write(f"    크기: {tile['bbox_width']}x{tile['bbox_height']}\n")
                    f.write(f"    픽셀 수: {tile['pixel_count']} ({tile['coverage']:.1f}% 채워짐)\n")
                    f.write(f"    바운딩 박스: ({tile['bbox_min_x']}, {tile['bbox_min_y']}, {tile['bbox_max_x']}, {tile['bbox_max_y']})\n\n")

            elif result['type'] == 'animated':
                f.write(f"이미지 크기: {data['width']}x{data['height']}\n")
                f.write(f"프레임 수: {data['frame_count']}\n")
                f.write(f"프레임 크기: {data['frame_width']}x{data['frame_height']}\n\n")

                for frame in data['frames']:
                    f.write(f"  프레임 {frame['frame_index']}:\n")
                    f.write(f"    유효 영역: X({frame['bbox_min_x']}~{frame['bbox_max_x']}), Y({frame['bbox_min_y']}~{frame['bbox_max_y']})\n")
                    f.write(f"    크기: {frame['bbox_width']}x{frame['bbox_height']}\n")
                    f.write(f"    픽셀 수: {frame['pixel_count']}\n")
                    f.write(f"    평균 알파: {frame['avg_alpha']:.1f}\n")
                    f.write(f"    바운딩 박스: ({frame['bbox_min_x']}, {frame['bbox_min_y']}, {frame['bbox_max_x']}, {frame['bbox_max_y']})\n\n")

            elif result['type'] == 'single' and data:
                f.write(f"이미지 크기: {data['width']}x{data['height']}\n")
                f.write(f"유효 영역: X({data['bbox_min_x']}~{data['bbox_max_x']}), Y({data['bbox_min_y']}~{data['bbox_max_y']})\n")
                f.write(f"크기: {data['bbox_width']}x{data['bbox_height']}\n")
                f.write(f"픽셀 수: {data['pixel_count']} ({data['coverage']:.1f}% 채워짐)\n")
                f.write(f"바운딩 박스: ({data['bbox_min_x']}, {data['bbox_min_y']}, {data['bbox_max_x']}, {data['bbox_max_y']})\n")
                f.write(f"주요 색상:\n")
                for color, count in data['top_colors']:
                    f.write(f"  - {color}: {count}픽셀\n")
                f.write("\n")

    # JSON 형식으로도 저장
    json_output_path = os.path.join(resource_dir, 'tile_bounds_detailed.json')
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n분석 완료!")
    print(f"텍스트 결과: {output_path}")
    print(f"JSON 결과: {json_output_path}")
    print(f"총 {len(results)}개 타일 이미지 분석됨")

if __name__ == '__main__':
    main()
