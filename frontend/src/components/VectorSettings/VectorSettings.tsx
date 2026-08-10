import { useId, useState } from "react";
import { Dropdown, Option, OptionOnSelectData, SelectionEvents } from "@fluentui/react-components";

import styles from "./VectorSettings.module.css";
import { RetrievalMode } from "../../api";
import { HelpCallout } from "../../components/HelpCallout";
import { toolTipText } from "../../i18n/tooltips.js";

interface Props {
    defaultRetrievalMode: RetrievalMode;
    updateRetrievalMode: (retrievalMode: RetrievalMode) => void;
}

export const VectorSettings = ({ updateRetrievalMode, defaultRetrievalMode }: Props) => {
    const [retrievalMode, setRetrievalMode] = useState<RetrievalMode>(defaultRetrievalMode);
    const retrievalModeId = useId();
    const retrievalModeFieldId = useId();

    const onRetrievalModeChange = (_ev: SelectionEvents, data: OptionOnSelectData) => {
        const mode = (data.optionValue as RetrievalMode) || RetrievalMode.Hybrid;
        setRetrievalMode(mode);
        updateRetrievalMode(mode);
    };

    return (
        <div className={styles.container} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <HelpCallout labelId={retrievalModeId} fieldId={retrievalModeFieldId} helpText={toolTipText.retrievalMode} label="Retrieval mode" />
            <Dropdown
                id={retrievalModeFieldId}
                aria-labelledby={retrievalModeId}
                selectedOptions={[retrievalMode.toString()]}
                value={
                    retrievalMode === RetrievalMode.Hybrid
                        ? "RAG with Vector Search"
                        : retrievalMode === RetrievalMode.Vectors
                          ? "Vector Search"
                          : "Keyword Search"
                }
                onOptionSelect={onRetrievalModeChange}
            >
                <Option value={RetrievalMode.Hybrid}>RAG with Vector Search</Option>
                <Option value={RetrievalMode.Vectors}>Vector Search</Option>
                <Option value={RetrievalMode.Text}>Keyword Search</Option>
            </Dropdown>
        </div>
    );
};
