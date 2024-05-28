type HtmlParsedAnswer = {
    answerHtml: string;
};

export function parseAnswerToHtml(answer: string): HtmlParsedAnswer {
    // trim any whitespace from the end of the answer after removing follow-up questions
    let parsedAnswer = answer.trim();

    const parts = parsedAnswer.split(/\[([^\]]+)\]/g);

    const fragments: string[] = parts.map((part, index) => {
        return part;
    });

    return {
        answerHtml: fragments.join("")
    };
}
