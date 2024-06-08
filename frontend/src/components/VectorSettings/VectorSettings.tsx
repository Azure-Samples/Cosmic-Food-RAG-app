import { useState } from "react";
import { Stack, IDropdownOption, Dropdown, IDropdownProps } from "@fluentui/react";
import { useId } from "@fluentui/react-hooks";

import styles from "./VectorSettings.module.css";
import { RetrievalMode } from "../../api";
import { HelpCallout } from "../../components/HelpCallout";
import { toolTipText } from "../../i18n/tooltips.js";

interface Props {
    defaultRetrievalMode: RetrievalMode;
    updateRetrievalMode: (retrievalMode: RetrievalMode) => void;
}

export const VectorSettings = ({ updateRetrievalMode, defaultRetrievalMode }: Props) => {
    const [retrievalMode, setRetrievalMode] = useState<RetrievalMode>(RetrievalMode.Hybrid);
    const retrievalModeId = useId("retrievalMode");
    const retrievalModeFieldId = useId("retrievalModeField");

    const onRetrievalModeChange = (_ev: React.FormEvent<HTMLDivElement>, option?: IDropdownOption<RetrievalMode> | undefined) => {
        setRetrievalMode(option?.data || RetrievalMode.Hybrid);
        updateRetrievalMode(option?.data || RetrievalMode.Hybrid);
    };

    return (
        <Stack className={styles.container} tokens={{ childrenGap: 10 }}>
            <Dropdown
                id={retrievalModeFieldId}
                label="Retrieval mode"
                selectedKey={defaultRetrievalMode.toString()}
                options={[
                    { key: "rag", text: "RAG with Vector Search", selected: retrievalMode == RetrievalMode.Hybrid, data: RetrievalMode.Hybrid },
                    { key: "vector", text: "Vector Search", selected: retrievalMode == RetrievalMode.Vectors, data: RetrievalMode.Vectors },
                    { key: "keyword", text: "Keyword Search", selected: retrievalMode == RetrievalMode.Text, data: RetrievalMode.Text }
                ]}
                required
                onChange={onRetrievalModeChange}
                aria-labelledby={retrievalModeId}
                onRenderLabel={(props: IDropdownProps | undefined) => (
                    <HelpCallout labelId={retrievalModeId} fieldId={retrievalModeFieldId} helpText={toolTipText.retrievalMode} label={props?.label} />
                )}
            />
        </Stack>
    );
};
