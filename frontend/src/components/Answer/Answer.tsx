import { useMemo } from "react";
import { Button } from "@fluentui/react-components";
import { Lightbulb24Regular, ClipboardTaskListLtr24Regular } from "@fluentui/react-icons";
import DOMPurify from "dompurify";

import styles from "./Answer.module.css";

import { ChatCompletionResponse } from "../../api";
import { parseAnswerToHtml } from "./AnswerParser";
import { AnswerIcon } from "./AnswerIcon";
import { SpeechOutput } from "./SpeechOutput";

interface Props {
    answer: ChatCompletionResponse;
    isSelected?: boolean;
    isStreaming: boolean;
    onThoughtProcessClicked: () => void;
    onSupportingContentClicked: () => void;
}

export const Answer = ({ answer, isSelected, isStreaming, onThoughtProcessClicked, onSupportingContentClicked }: Props) => {
    const messageContent = answer.message.content;
    const parsedAnswer = useMemo(() => parseAnswerToHtml(messageContent, isStreaming), [answer]);

    const sanitizedAnswerHtml = DOMPurify.sanitize(parsedAnswer.answerHtml);

    return (
        <div
            className={`${styles.answerContainer} ${isSelected && styles.selected}`}
            style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}
        >
            <div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <AnswerIcon />
                    <div>
                        <Button
                            appearance="transparent"
                            style={{ color: "black" }}
                            icon={<Lightbulb24Regular />}
                            title="Show thought process"
                            aria-label="Show thought process"
                            onClick={() => onThoughtProcessClicked()}
                            disabled={!answer.context.thoughts?.length}
                        />
                        <Button
                            appearance="transparent"
                            style={{ color: "black" }}
                            icon={<ClipboardTaskListLtr24Regular />}
                            title="Show supporting content"
                            aria-label="Show supporting content"
                            onClick={() => onSupportingContentClicked()}
                            disabled={!answer.context.data_points?.length}
                        />
                        <SpeechOutput answer={sanitizedAnswerHtml} />
                    </div>
                </div>
            </div>

            <div style={{ flexGrow: 1 }}>
                <div className={styles.answerText} dangerouslySetInnerHTML={{ __html: sanitizedAnswerHtml }}></div>
            </div>
        </div>
    );
};
