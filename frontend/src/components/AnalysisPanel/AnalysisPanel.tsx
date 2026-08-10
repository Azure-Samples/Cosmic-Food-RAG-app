import { Tab, TabList, SelectTabEvent, SelectTabData } from "@fluentui/react-components";

import { SupportingContent } from "../SupportingContent";
import { ChatCompletionResponse } from "../../api";
import { AnalysisPanelTabs } from "./AnalysisPanelTabs";
import { ThoughtProcess } from "./ThoughtProcess";

interface Props {
    className: string;
    activeTab: AnalysisPanelTabs;
    onActiveTabChanged: (tab: AnalysisPanelTabs) => void;
    answer: ChatCompletionResponse;
}

export const AnalysisPanel = ({ answer, activeTab, className, onActiveTabChanged }: Props) => {
    const isDisabledThoughtProcessTab: boolean = !answer.context.thoughts;
    const isDisabledSupportingContentTab: boolean = !answer.context.data_points;

    const onTabSelect = (_ev: SelectTabEvent, data: SelectTabData) => onActiveTabChanged(data.value as AnalysisPanelTabs);

    return (
        <div className={className}>
            <TabList selectedValue={activeTab} onTabSelect={onTabSelect}>
                <Tab value={AnalysisPanelTabs.ThoughtProcessTab} disabled={isDisabledThoughtProcessTab}>
                    Thought process
                </Tab>
                <Tab value={AnalysisPanelTabs.SupportingContentTab} disabled={isDisabledSupportingContentTab}>
                    Supporting content
                </Tab>
            </TabList>
            {activeTab === AnalysisPanelTabs.ThoughtProcessTab && <ThoughtProcess thoughts={answer.context.thoughts || []} />}
            {activeTab === AnalysisPanelTabs.SupportingContentTab && <SupportingContent supportingContent={answer.context.data_points} />}
        </div>
    );
};
