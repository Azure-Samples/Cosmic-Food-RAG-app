import { useRef, useState, useEffect } from "react";
import { Panel, DefaultButton, SpinButton, Slider } from "@fluentui/react";
import cosmos from "../../assets/FeaturedDefault.png";

import styles from "./Chat.module.css";

import { chatApi, RetrievalMode, ChatAppResponse, ChatAppResponseOrError, ChatAppRequest, ResponseMessage, JSONDataPoint } from "../../api";
import { Answer, AnswerError, AnswerLoading } from "../../components/Answer";
import { QuestionInput } from "../../components/QuestionInput";
import { ExampleList } from "../../components/Example";
import { UserChatMessage } from "../../components/UserChatMessage";
import { AnalysisPanel, AnalysisPanelTabs } from "../../components/AnalysisPanel";
import { SettingsButton } from "../../components/SettingsButton";
import { CartButton } from "../../components/CartButton";
import { ClearChatButton } from "../../components/ClearChatButton";
import { VectorSettings } from "../../components/VectorSettings";
import { BuyModal } from "../../components/BuyModal";

const Chat = () => {
    const [isConfigPanelOpen, setIsConfigPanelOpen] = useState(false);
    const [isCartOpen, setIsCartOpen] = useState(false);
    const [temperature, setTemperature] = useState<number>(0.3);
    const [retrieveCount, setRetrieveCount] = useState<number>(3);
    const [scoreThreshold, setScoreThreshold] = useState<number>(0.5);
    const [retrievalMode, setRetrievalMode] = useState<RetrievalMode>(RetrievalMode.Hybrid);

    const lastQuestionRef = useRef<string>("");

    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isBuy, setIsBuy] = useState<boolean>(false);
    const [address, setAddress] = useState<string>("");
    const [cartItems, setCartItems] = useState<string[]>([]);
    const [error, setError] = useState<unknown>();

    const [activeAnalysisPanelTab, setActiveAnalysisPanelTab] = useState<AnalysisPanelTabs | undefined>(undefined);

    const [selectedAnswer, setSelectedAnswer] = useState<number>(0);
    const [latestItems, setLatestItems] = useState<JSONDataPoint[]>([]);
    const [answers, setAnswers] = useState<[user: string, response: ChatAppResponse][]>([]);
    const [sessionState, setSessionState] = useState<string | null>(null);

    const checkthenMakeApiRequest = async (question: string) => {
        lastQuestionRef.current = question;
        if (question.match(/buy/)) {
            setIsBuy(true);
            return;
        }
        makeApiRequest(question);
    };

    const makeApiRequest = async (question: string) => {
        lastQuestionRef.current = question;

        error && setError(undefined);
        setIsLoading(true);
        setActiveAnalysisPanelTab(undefined);

        try {
            const messages: ResponseMessage[] = answers.flatMap(a => [
                { content: a[0], role: "user" },
                { content: a[1].choices[0].message.content, role: "assistant" }
            ]);

            const request: ChatAppRequest = {
                messages: [...messages, { content: question, role: "user" }],
                context: {
                    overrides: {
                        top: retrieveCount,
                        temperature: temperature,
                        score_threshold: scoreThreshold,
                        retrieval_mode: retrievalMode
                    }
                },
                session_state: sessionState ? sessionState : null
            };

            const response = await chatApi(request);
            if (!response.body) {
                throw Error("No response body");
            }
            const parsedResponse: ChatAppResponseOrError = await response.json();
            if (response.status > 299 || !response.ok) {
                throw Error(parsedResponse.error || "Unknown error");
            }
            setAnswers([...answers, [question, parsedResponse as ChatAppResponse]]);
            setSessionState(parsedResponse?.choices ? parsedResponse.choices[0].session_state : null);
            setLatestItems(parsedResponse?.choices ? parsedResponse.choices[0].context.data_points.json : []);
        } catch (e) {
            setError(e);
        } finally {
            setIsLoading(false);
        }
    };

    const clearChat = () => {
        lastQuestionRef.current = "";
        error && setError(undefined);
        setActiveAnalysisPanelTab(undefined);
        setAnswers([]);
        setIsLoading(false);
    };

    const onTemperatureChange = (
        newValue: number,
        range?: [number, number],
        event?: React.MouseEvent | React.TouchEvent | MouseEvent | TouchEvent | React.KeyboardEvent
    ) => {
        setTemperature(newValue);
    };

    const onScoreThresholdChange = (
        newValue: number,
        range?: [number, number],
        event?: React.MouseEvent | React.TouchEvent | MouseEvent | TouchEvent | React.KeyboardEvent
    ) => {
        setScoreThreshold(newValue);
    };

    const onRetrieveCountChange = (_ev?: React.SyntheticEvent<HTMLElement, Event>, newValue?: string) => {
        setRetrieveCount(parseInt(newValue || "3"));
    };

    const onExampleClicked = (example: string) => {
        makeApiRequest(example);
    };

    const onToggleTab = (tab: AnalysisPanelTabs, index: number) => {
        if (activeAnalysisPanelTab === tab && selectedAnswer === index) {
            setActiveAnalysisPanelTab(undefined);
        } else {
            setActiveAnalysisPanelTab(tab);
        }

        setSelectedAnswer(index);
    };

    return (
        <div className={styles.container}>
            <div className={styles.commandsContainer}>
                <CartButton className={styles.commandButton} onClick={() => setIsCartOpen(!isCartOpen)} />
                <ClearChatButton className={styles.commandButton} onClick={clearChat} disabled={!lastQuestionRef.current || isLoading} />
                <SettingsButton className={styles.commandButton} onClick={() => setIsConfigPanelOpen(!isConfigPanelOpen)} />
            </div>
            <div className={styles.chatRoot}>
                <div className={styles.chatContainer}>
                    {!lastQuestionRef.current ? (
                        <div className={styles.chatEmptyState}>
                            <img src={cosmos} alt="Cosmos logo" aria-label="Cosmos logo" width="100px" height="100px" className={styles.githubLogo} />
                            <h1 className={styles.chatEmptyStateTitle}>FlavorGenius: Chat, Input, Discover</h1>
                            <h2 className={styles.chatEmptyStateSubtitle}>Ask anything or try an example</h2>
                            <ExampleList onExampleClicked={onExampleClicked} />
                        </div>
                    ) : (
                        <div className={styles.chatMessageStream}>
                            {answers.map((answer, index) => (
                                <div key={index}>
                                    <UserChatMessage message={answer[0]} />
                                    <div className={styles.chatMessageGpt}>
                                        <Answer
                                            key={index}
                                            answer={answer[1]}
                                            isSelected={selectedAnswer === index && activeAnalysisPanelTab !== undefined}
                                            onThoughtProcessClicked={() => onToggleTab(AnalysisPanelTabs.ThoughtProcessTab, index)}
                                            onSupportingContentClicked={() => onToggleTab(AnalysisPanelTabs.SupportingContentTab, index)}
                                        />
                                    </div>
                                </div>
                            ))}
                            {isLoading && (
                                <>
                                    <UserChatMessage message={lastQuestionRef.current} />
                                    <div className={styles.chatMessageGptMinWidth}>
                                        <AnswerLoading />
                                    </div>
                                </>
                            )}
                            {isBuy ? (
                                <>
                                    <BuyModal
                                        isBuy={isBuy}
                                        setIsBuy={setIsBuy}
                                        address={address}
                                        setAddress={setAddress}
                                        latestItems={latestItems}
                                        cartItems={cartItems}
                                        setCartItems={setCartItems}
                                    />
                                </>
                            ) : null}
                            {error ? (
                                <>
                                    <UserChatMessage message={lastQuestionRef.current} />
                                    <div className={styles.chatMessageGptMinWidth}>
                                        <AnswerError error={error.toString()} onRetry={() => makeApiRequest(lastQuestionRef.current)} />
                                    </div>
                                </>
                            ) : null}
                        </div>
                    )}

                    <div className={styles.chatInput}>
                        <QuestionInput
                            clearOnSend
                            placeholder="Type a new question (e.g. Are there any high protein dishes available?)"
                            disabled={isLoading}
                            onSend={question => checkthenMakeApiRequest(question)}
                        />
                    </div>
                </div>

                {answers.length > 0 && activeAnalysisPanelTab && (
                    <AnalysisPanel
                        className={styles.chatAnalysisPanel}
                        onActiveTabChanged={x => onToggleTab(x, selectedAnswer)}
                        answer={answers[selectedAnswer][1]}
                        activeTab={activeAnalysisPanelTab}
                    />
                )}

                <Panel
                    headerText="Cart Items"
                    isOpen={isCartOpen}
                    isBlocking={false}
                    onDismiss={() => setIsCartOpen(false)}
                    closeButtonAriaLabel="Close"
                    onRenderFooterContent={() => <DefaultButton onClick={() => setIsCartOpen(false)}>Close</DefaultButton>}
                    isFooterAtBottom={true}
                >
                    <div>
                        {cartItems.map((item, index) => (
                            <h4 key={index}>- {item}</h4>
                        ))}
                    </div>
                </Panel>
                <Panel
                    headerText="Configure answer generation"
                    isOpen={isConfigPanelOpen}
                    isBlocking={false}
                    onDismiss={() => setIsConfigPanelOpen(false)}
                    closeButtonAriaLabel="Close"
                    onRenderFooterContent={() => <DefaultButton onClick={() => setIsConfigPanelOpen(false)}>Close</DefaultButton>}
                    isFooterAtBottom={true}
                >
                    <Slider
                        className={styles.chatSettingsSeparator}
                        label="Temperature"
                        min={0}
                        max={1}
                        step={0.1}
                        defaultValue={temperature}
                        onChange={onTemperatureChange}
                        showValue
                        snapToStep
                    />

                    <Slider
                        className={styles.chatSettingsSeparator}
                        label="Similarity Score Threshold"
                        min={0}
                        max={1}
                        step={0.1}
                        defaultValue={scoreThreshold}
                        onChange={onScoreThresholdChange}
                        showValue
                        snapToStep
                    />

                    <SpinButton
                        className={styles.chatSettingsSeparator}
                        label="Retrieve this many search results:"
                        min={1}
                        max={20}
                        defaultValue={retrieveCount.toString()}
                        onChange={onRetrieveCountChange}
                    />

                    <VectorSettings
                        defaultRetrievalMode={retrievalMode}
                        updateRetrievalMode={(retrievalMode: RetrievalMode) => setRetrievalMode(retrievalMode)}
                    />
                </Panel>
            </div>
        </div>
    );
};

export default Chat;
