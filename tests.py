from unittest import TestCase, main

from parsers import ScoreBoard


class TestScoreBoard(TestCase):

    body = """
    <div class="user-score-board">
        <a class="user-score-box" href="https://www.creditkarma.com/myfinances/scores/transunion">
            <div id="" class="retrovision-container">
                <svg class="thermodial-svg" viewBox="" style="width:90%;height:auto;" data-reactroot="" data-reactid="1" data-react-checksum="">
                    <text text-anchor="middle" x="" y="" style="font-size:1.5rem;font-weight:500;" fill="#404345" data-reactid="17">700</text>
                    <text text-anchor="middle" x="" y="" style="font-size:0.5rem;font-weight:500;" fill="#404345" data-reactid="22">Good</text>
                </svg>
            </div>
        </a>
    </div>
    """

    def setUp(self):
        self.score_board = ScoreBoard.from_response_content(self.body)[0]

    def test_bureau_name(self):
        self.assertEqual(self.score_board.bureau_name, 'transunion')

    def test_score(self):
        self.assertEqual(self.score_board.score, 700)

    def test_hyperlink(self):
        self.assertEqual(self.score_board.hyperlink, 'https://www.creditkarma.com/myfinances/scores/transunion')

    def test_category(self):
        self.assertEqual(self.score_board.category, 'Good')


if __name__ == '__main__':
    main()
