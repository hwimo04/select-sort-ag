import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 웹 앱 및 외부 환경에서의 CORS 요청 허용
CORS(app)

def selection_sort_trace(arr):
    """
    단순 선택 정렬을 수행하면서 각 탐색 및 교환 시점의 상태를 단계별로 기록합니다.
    - arr: 정렬할 숫자 리스트
    - returns: (단계별 스냅샷 리스트, 최종 정렬 완료 리스트)
    """
    steps = []
    data = list(arr)
    n = len(data)

    # 0단계: 초기 상태 스냅샷 저장
    steps.append({
        "step": 0,
        "pass": 0,
        "array": list(data),
        "target_index": -1,       # 자리가 확정될 대상 인덱스
        "min_index": -1,          # 현재 탐색된 최솟값 인덱스
        "comparing_index": -1,    # 비교 중인 인덱스
        "swapped": False,
        "description": "정렬 시작 전 초기 배열 상태입니다."
    })

    step_count = 1

    # 외부 루프: i번째 자리에 들어갈 최솟값을 찾음 (0부터 n-2까지)
    for i in range(n - 1):
        min_idx = i  # 현재 범위의 첫 번째 원소를 최솟값으로 가정

        # 패스 시작 알림 스냅샷
        steps.append({
            "step": step_count,
            "pass": i + 1,
            "array": list(data),
            "target_index": i,
            "min_index": min_idx,
            "comparing_index": -1,
            "swapped": False,
            "description": f"[{i + 1}회차 시작] 인덱스 {i}에 배치할 최솟값 탐색을 시작합니다. (초기 최솟값: {data[min_idx]})"
        })
        step_count += 1

        # 내부 루프: i+1부터 끝까지 순회하며 실제 최솟값의 위치(min_idx)를 탐색
        for j in range(i + 1, n):
            # 비교 스냅샷
            desc = f"인덱스 {j}(값: {data[j]})와 현재 최솟값 인덱스 {min_idx}(값: {data[min_idx]}) 비교"
            
            if data[j] < data[min_idx]:
                min_idx = j
                desc += f" ➔ 새로운 최솟값 발견! (인덱스 {min_idx}, 값: {data[min_idx]})"
            else:
                desc += " ➔ 최솟값 변동 없음"

            steps.append({
                "step": step_count,
                "pass": i + 1,
                "array": list(data),
                "target_index": i,
                "min_index": min_idx,
                "comparing_index": j,
                "swapped": False,
                "description": desc
            })
            step_count += 1

        # 탐색 완료 후 교환(Swap): 최솟값 위치가 시작 위치(i)와 다를 때만 교환
        is_swapped = (min_idx != i)
        if is_swapped:
            data[i], data[min_idx] = data[min_idx], data[i]
            swap_desc = f"[{i + 1}회차 종료] 최솟값(인덱스 {min_idx}, 값 {data[i]})을 인덱스 {i}(이전 값 {data[min_idx]})와 교환하여 정렬 위치 확정."
        else:
            swap_desc = f"[{i + 1}회차 종료] 이미 인덱스 {i}의 값이 최솟값이므로 교환 없이 위치 확정."

        steps.append({
            "step": step_count,
            "pass": i + 1,
            "array": list(data),
            "target_index": i,
            "min_index": min_idx,
            "comparing_index": -1,
            "swapped": is_swapped,
            "description": swap_desc
        })
        step_count += 1

    # 최종 완료 스냅샷
    steps.append({
        "step": step_count,
        "pass": n - 1,
        "array": list(data),
        "target_index": -1,
        "min_index": -1,
        "comparing_index": -1,
        "swapped": False,
        "description": "모든 회차가 종료되어 단순 선택 정렬이 완료되었습니다."
    })

    return steps, data

@app.route('/sort', methods=['POST'])
def handle_sort():
    """
    단순 선택 정렬 수행 API 엔드포인트
    Request 예시: {"numbers": [29, 10, 14, 37, 13]}
    """
    try:
        content = request.get_json(silent=True)
        if not content or 'numbers' not in content:
            return jsonify({
                "status": "error",
                "message": "JSON 형식의 'numbers' 배열 필드가 필요합니다."
            }), 400

        numbers = content['numbers']
        if not isinstance(numbers, list) or not all(isinstance(x, (int, float)) for x in numbers):
            return jsonify({
                "status": "error",
                "message": "'numbers'는 숫자들의 배열이어야 합니다."
            }), 400

        # 선택 정렬 및 단계별 스냅샷 생성
        steps, sorted_result = selection_sort_trace(numbers)

        # 단순 선택 정렬 복잡도 정의
        complexity = {
            "algorithm": "단순 선택 정렬 (Selection Sort)",
            "time_best": "O(N²)",
            "time_average": "O(N²)",
            "time_worst": "O(N²)",
            "space": "O(1) (제자리 정렬, In-place)",
            "stability": "불안정 정렬 (Unstable Sort)"
        }

        # 괄호 닫힘 오류가 발생하지 않도록 완전한 JSON 응답 반환
        return jsonify({
            "status": "success",
            "original": numbers,
            "sorted": sorted_result,
            "total_steps": len(steps) - 1,
            "complexity": complexity,
            "steps": steps
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Cloud Run 상태 체크용 엔드포인트"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Cloud Run에서 전달하는 PORT 환경변수 사용
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
