import json
from pathlib import Path

STATE = Path(__file__).resolve().parent / 'state.json'

class Quiz:
    """퀴즈 문제와 선택지, 정답을 관리하는 클래스."""

    def __init__(self, question, choices, answer):
        self.question, self.choices, self.answer = question, choices, answer

    def show(self):
        print('\n' + self.question)
        for i, choice in enumerate(self.choices, 1):
            print(f'{i}. {choice}')

    def check(self, number):
        return number == self.answer

    def to_dict(self):
        return {'question': self.question, 'choices': self.choices, 'answer': self.answer}

DEFAULT = [
    Quiz('대한민국의 수도는?', ['서울', '부산', '대구', '광주'], 1),
    Quiz('제주도에 있는 유명한 산은?', ['설악산', '한라산', '지리산', '북한산'], 2),
    Quiz('해운대 해수욕장이 있는 도시는?', ['인천', '강릉', '부산', '여수'], 3),
    Quiz('불국사가 있는 도시는?', ['경주', '통영', '전주', '춘천'], 1),
    Quiz('전주에서 유명한 음식은?', ['밀면', '비빔밥', '닭갈비', '물회'], 2),
]

class QuizGame:
    """퀴즈 실행, 문제 추가, 점수 및 저장 기능을 관리하는 클래스."""

    def __init__(self):
        self.quizzes = list(DEFAULT)
        self.best_score = None
        self.load()

    def load(self):
        if not STATE.exists():
            return
        try:
            data = json.loads(STATE.read_text(encoding='utf-8'))
            quizzes = data['quizzes']
            score = data['best_score']
            if not isinstance(quizzes, list) or not all(
                isinstance(q, dict) and isinstance(q.get('question'), str) and q['question'].strip()
                and isinstance(q.get('choices'), list) and len(q['choices']) == 4
                and all(isinstance(c, str) and c.strip() for c in q['choices'])
                and type(q.get('answer')) is int and 1 <= q['answer'] <= 4
                for q in quizzes
            ) or not (score is None or (type(score) is int and 0 <= score <= 100)):
                raise ValueError('데이터 형식 오류')
            self.quizzes = [Quiz(**q) for q in quizzes]
            self.best_score = score
            print('저장된 데이터를 불러왔습니다.')
        except (OSError, ValueError, KeyError, TypeError, UnicodeError) as e:
            print(f'저장 파일 오류: {e}. 기본 데이터로 시작합니다.')

    def save(self):
        try:
            data = {'quizzes': [q.to_dict() for q in self.quizzes], 'best_score': self.best_score}
            STATE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        except OSError as e:
            print(f'저장 실패: {e}')

    def number(self, prompt, minimum, maximum):
        while True:
            raw = input(prompt).strip()
            if not raw:
                print('빈 입력입니다. 다시 입력하세요.')
                continue
            try:
                value = int(raw)
            except ValueError:
                print('숫자를 입력하세요.')
                continue
            if minimum <= value <= maximum:
                return value
            print(f'{minimum}~{maximum} 사이 숫자를 입력하세요.')

    def required_text(self, prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print('빈 내용은 입력할 수 없습니다.')
    def play(self):
        if not self.quizzes:
            print('등록된 퀴즈가 없습니다.')
            return

        correct = 0

        for i, quiz in enumerate(self.quizzes, 1):
            print(f'\n[문제 {i}/{len(self.quizzes)}]')
            quiz.show()

            answer = self.number('정답 (0: 메뉴로 돌아가기, 1~4): ', 0, 4)

            if answer == 0:
                print('퀴즈를 중단하고 메뉴로 돌아갑니다.')
                return

            if quiz.check(answer):
                print('정답입니다!')
                correct += 1
            else:
                print(f'오답입니다. 정답: {quiz.answer}번 ({quiz.choices[quiz.answer - 1]})')

        score = round(correct * 100 / len(self.quizzes))
        print(f'결과: {correct}/{len(self.quizzes)}문제 정답, {score}점')

        if self.best_score is None or score > self.best_score:
            self.best_score = score
            print('새로운 최고 점수!')

        self.save()
    

    def add(self):
        question = self.required_text('문제: ')
        choices = [self.required_text(f'선택지 {i}: ') for i in range(1, 5)]
        answer = self.number('정답 번호 (1~4): ', 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        self.save()
        print('퀴즈가 추가되었습니다.')

    def show_list(self):
        if not self.quizzes:
            print('등록된 퀴즈가 없습니다.')
        else:
            print(f'총 {len(self.quizzes)}개의 퀴즈가 있습니다.')
            for i, quiz in enumerate(self.quizzes, 1):
                print(f'{i}. {quiz.question}')

    def show_score(self):
        print('아직 기록이 없습니다.' if self.best_score is None else f'최고 점수: {self.best_score}점')

    def run(self):
        try:
            while True:
                print('\n=== 한국 여행 퀴즈 ===')
                print('1. 퀴즈 풀기\n2. 퀴즈 추가\n3. 퀴즈 목록\n4. 점수 확인\n5. 종료')
                menu = self.number('선택: ', 1, 5)
                if menu == 1:
                    self.play()
                elif menu == 2:
                    self.add()
                elif menu == 3:
                    self.show_list()
                elif menu == 4:
                    self.show_score()
                else:
                    break
        except (KeyboardInterrupt, EOFError):
            print('\n입력이 중단되어 안전하게 종료합니다.')
        finally:
            self.save()
        print('한국 여행 퀴즈를 이용해 주셔서 감사합니다.')     
        print('게임을 종료합니다.')

if __name__ == '__main__':
    QuizGame().run()
