import { useMemo } from "react";
import { Stack, IconButton } from "@fluentui/react";
import DOMPurify from "dompurify";

import styles from "./Answer.module.css";

import { ChatAppResponse } from "../../api";
import { parseAnswerToHtml } from "./AnswerParser";
import { AnswerIcon } from "./AnswerIcon";
import { SpeechOutput } from "./SpeechOutput";

interface Props {
    answer: ChatAppResponse;
    isSelected?: boolean;
    onThoughtProcessClicked: () => void;
    onSupportingContentClicked: () => void;
}

export const Answer = ({ answer, isSelected, onThoughtProcessClicked, onSupportingContentClicked }: Props) => {
    const messageContent = answer.choices[0].message.content;
    const parsedAnswer = useMemo(() => parseAnswerToHtml(messageContent), [answer]);

    const sanitizedAnswerHtml = DOMPurify.sanitize(parsedAnswer.answerHtml);

    return (
        <Stack className={`${styles.answerContainer} ${isSelected && styles.selected}`} verticalAlign="space-between">
            <Stack.Item>
                <Stack horizontal horizontalAlign="space-between">
                    <AnswerIcon />
                    <div>
                        <IconButton
                            style={{ color: "black" }}
                            iconProps={{ iconName: "Lightbulb" }}
                            title="Show thought process"
                            ariaLabel="Show thought process"
                            onClick={() => onThoughtProcessClicked()}
                            disabled={!answer.choices[0].context.thoughts?.length}
                        />
                        <IconButton
                            style={{ color: "black" }}
                            iconProps={{ iconName: "ClipboardList" }}
                            title="Show supporting content"
                            ariaLabel="Show supporting content"
                            onClick={() => onSupportingContentClicked()}
                            disabled={!answer.choices[0].context.data_points}
                        />
                        <SpeechOutput answer={sanitizedAnswerHtml} />
                    </div>
                </Stack>
            </Stack.Item>

            <Stack.Item grow>
                <div className={styles.answerText} dangerouslySetInnerHTML={{ __html: sanitizedAnswerHtml }}></div>
            </Stack.Item>
        </Stack>
    );
};
