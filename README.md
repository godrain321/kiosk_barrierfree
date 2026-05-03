📌 Project Overview
본 프로젝트는 시각장애인의 독립적인 키오스크 이용을 돕기 위해 음성 안내와 제스처 인식, 햅틱 인터페이스를 결합한 안내 시스템입니다. 출입문 진입부터 메뉴 결제까지의 전 과정을 비시각적 피드백으로 설계하였습니다.

# Demo video
1. Full System Operation (excluding Proximity Sensor)
   https://www.youtube.com/watch?v=JtLEo4CAmX4
2. Proximity Sensor Integration Test
   https://www.youtube.com/shorts/Xr2QyoMLNQA
   
Note: 본 프로젝트는 시각장애인을 위한 키오스크와 주문 완료 후 자율주행 모듈을 통한 안내까지를 목적으로 하였으나 기존 베리어 프리 키오스크가 현재 매우 상용화되었고 창의성이 떨어진다고 판단하여 중단함. 하지만 이 프로젝트를 진행하며 자율주행에 대해 공부했던 지식을 바탕으로 화재대피로봇제작을 목표로 잡음. 

⚙️ System Workflow (Core Logic)
1. Entrance & Guidance (진입 감지 및 안내)

문에 설치된 근접 센서(Proximity Sensor)가 물체(문)를 인식하지 못할 경우 '문 열림'으로 판단합니다.

진입이 확인되면 즉시 키오스크의 위치를 알리는 음성 안내("어서오세요. 키오스크는 출입문 오른쪽에 있습니다.")를 출력합니다.

2. User Interaction (사용자 인식 및 모드 전환)

Eye Tracking: 카메라를 통해 사용자의 눈이 3초간 인식되면 서비스 대기 상태로 전환합니다.

Gesture Recognition: YOLOv5 모델을 사용하여 사용자가 가슴 앞에 '주먹'을 쥐는 제스처를 인식하면, 자동으로 시각장애인 전용 모드를 활성화합니다.

3. Menu Navigation (메뉴 탐색)

사용자는 정면에 위치한 조이스틱을 조작하여 메뉴를 탐색합니다.

Audio Feedback: 조이스틱의 움직임에 따라 선택된 메뉴명과 가격을 실시간으로 음성 안내합니다.

4. Selection & Confirmation (주문 확정 로직)

Click Event: 조이스틱 클릭 시 해당 메뉴의 상세 정보를 읽어주며 최종 주문 의사를 확인합니다.

Double-Check Logic: 오동작 방지를 위해 한 번 더 클릭해야 주문이 확정되도록 설계하였으며, 취소를 원할 경우 조이스틱을 임의의 방향으로 움직여 이전 단계로 복귀합니다.

5. Completion (주문 완료)

최종 확인이 완료되면 주문 성공 메시지를 음성으로 출력하며 프로세스를 종료합니다.
