import { useState, useEffect } from "react";
import { Button, Textarea, TextareaOnChangeData, Tooltip } from "@fluentui/react-components";
import { Send28Filled } from "@fluentui/react-icons";

import styles from "./QuestionInput.module.css";
import { SpeechInput } from "./SpeechInput";

interface Props {
    onSend: (question: string) => void;
    disabled: boolean;
    initQuestion?: string;
    placeholder?: string;
    clearOnSend?: boolean;
}

export const QuestionInput = ({ onSend, disabled, placeholder, clearOnSend, initQuestion }: Props) => {
    const [question, setQuestion] = useState<string>("");

    useEffect(() => {
        if (initQuestion) {
            setQuestion(initQuestion);
        }
    }, [initQuestion]);

    const sendQuestion = () => {
        if (disabled || !question.trim()) {
            return;
        }

        onSend(question);

        if (clearOnSend) {
            setQuestion("");
        }
    };

    const onEnterPress = (ev: React.KeyboardEvent<Element>) => {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            sendQuestion();
        }
    };

    const onQuestionChange = (_ev: React.ChangeEvent<HTMLTextAreaElement>, data: TextareaOnChangeData) => {
        if (!data.value) {
            setQuestion("");
        } else if (data.value.length <= 1000) {
            setQuestion(data.value);
        }
    };

    const sendQuestionDisabled = disabled || !question.trim();

    return (
        <div className={styles.questionInputContainer}>
            <Textarea
                className={styles.questionInputTextArea}
                placeholder={placeholder}
                resize="none"
                value={question}
                onChange={onQuestionChange}
                onKeyDown={onEnterPress}
            />
            <div className={styles.questionInputButtonsContainer}>
                <Tooltip content="Submit question" relationship="label">
                    <Button size="large" icon={<Send28Filled primaryFill="rgba(115, 118, 225, 1)" />} disabled={sendQuestionDisabled} onClick={sendQuestion} />
                </Tooltip>
            </div>
            <SpeechInput updateQuestion={setQuestion} />
        </div>
    );
};
