import { useRef, useState, useEffect, useId } from "react";
import {
    Checkbox,
    CheckboxOnChangeData,
    OverlayDrawer,
    DrawerHeader,
    DrawerHeaderTitle,
    DrawerBody,
    DrawerFooter,
    Button,
    Input,
    InputOnChangeData
} from "@fluentui/react-components";
import { Dismiss24Regular } from "@fluentui/react-icons";
import documentDB from "../../assets/FeaturedDefault.png";

import styles from "./Chat.module.css";

import { RetrievalMode, ChatCompletionResponse, ChatCompletionDeltaResponse, ChatAppRequestOptions, DataPoint } from "../../api";
import { AIChatProtocolClient, AIChatMessage } from "@microsoft/ai-chat-protocol";
import { Answer, AnswerError, AnswerLoading } from "../../components/Answer";
import { QuestionInput } from "../../components/QuestionInput";
import { ExampleList } from "../../components/Example";
import { UserChatMessage } from "../../components/UserChatMessage";
import { HelpCallout } from "../../components/HelpCallout";
import { AnalysisPanel, AnalysisPanelTabs } from "../../components/AnalysisPanel";
import { SettingsButton } from "../../components/SettingsButton";
import { CartButton } from "../../components/CartButton";
import { ClearChatButton } from "../../components/ClearChatButton";
import { VectorSettings } from "../../components/VectorSettings";
import { BuyModal } from "../../components/BuyModal";
import { toolTipText } from "../../i18n/tooltips.js";

const Chat = () => {
    const [isConfigPanelOpen, setIsConfigPanelOpen] = useState(false);
    const [isCartOpen, setIsCartOpen] = useState(false);
    const [temperature, setTemperature] = useState<number>(0.3);
    const [retrieveCount, setRetrieveCount] = useState<number>(3);
    const [scoreThreshold, setScoreThreshold] = useState<number>(0);
    const [retrievalMode, setRetrievalMode] = useState<RetrievalMode>(RetrievalMode.Hybrid);

    const lastQuestionRef = useRef<string>("");
    const chatMessageStreamEnd = useRef<HTMLDivElement | null>(null);

    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isStreaming, setIsStreaming] = useState<boolean>(false);
    const [shouldStream, setShouldStream] = useState<boolean>(false);
    const [isBuy, setIsBuy] = useState<boolean>(false);
    const [address, setAddress] = useState<string>("");
    const [cartItems, setCartItems] = useState<string[]>([]);
    const [error, setError] = useState<unknown>();

    const [activeAnalysisPanelTab, setActiveAnalysisPanelTab] = useState<AnalysisPanelTabs | undefined>(undefined);

    const [selectedAnswer, setSelectedAnswer] = useState<number>(0);
    const [latestItems, setLatestItems] = useState<DataPoint[]>([]);
    const [answers, setAnswers] = useState<[user: string, response: ChatCompletionResponse][]>([]);
    const [sessionState, setSessionState] = useState<object | null>(null);

    const [streamedAnswers, setStreamedAnswers] = useState<[user: string, response: ChatCompletionResponse][]>([]);

    const handleAsyncResponse = async (question: string, answers: [string, ChatCompletionResponse][], result: AsyncIterable<ChatCompletionDeltaResponse>) => {
        let answer = "";
        const chatCompletion: ChatCompletionResponse = {
            context: {
                data_points: [],
                thoughts: []
            },
            message: { content: "", role: "assistant" }
        };
        const updateState = (newContent: string) => {
            return new Promise(resolve => {
                setTimeout(() => {
                    answer += newContent;
                    // We need to create a new object to trigger a re-render
                    const latestCompletion: ChatCompletionResponse = {
                        ...chatCompletion,
                        message: { content: answer, role: chatCompletion.message.role }
                    };
                    setStreamedAnswers([...answers, [question, latestCompletion]]);
                    resolve(null);
                }, 33);
            });
        };
        try {
            setIsStreaming(true);
            for await (const response of result) {
                if (response.context) {
                    chatCompletion.context = {
                        ...chatCompletion.context,
                        ...response.context
                    };
                }
                if (response.delta && response.delta.role) {
                    chatCompletion.message.role = response.delta.role;
                }
                if (response.delta && response.delta.content) {
                    setIsLoading(false);
                    await updateState(response.delta.content);
                }
            }
        } finally {
            setIsStreaming(false);
        }
        chatCompletion.message.content = answer;
        return chatCompletion;
    };
    const makeApiRequest = async (question: string) => {
        lastQuestionRef.current = question;

        if (error) {
            setError(undefined);
        }
        setIsLoading(true);
        setActiveAnalysisPanelTab(undefined);
        try {
            const messages: AIChatMessage[] = answers.flatMap(a => [
                { content: a[0], role: "user" },
                { content: a[1].message.content, role: "assistant" }
            ]);

            const allMessages: AIChatMessage[] = [...messages, { content: question, role: "user" }];
            const options: ChatAppRequestOptions = {
                context: {
                    overrides: {
                        top: retrieveCount,
                        retrieval_mode: retrievalMode,
                        temperature: temperature,
                        score_threshold: scoreThreshold
                    }
                },
                sessionState: sessionState ? sessionState : null
            };
            const chatClient: AIChatProtocolClient = new AIChatProtocolClient("/chat");
            if (shouldStream) {
                const result = (await chatClient.getStreamedCompletion(allMessages, options)) as AsyncIterable<ChatCompletionDeltaResponse>;
                const parsedResponse = await handleAsyncResponse(question, answers, result);
                setAnswers([...answers, [question, parsedResponse]]);
                setSessionState(parsedResponse?.sessionState ? parsedResponse.sessionState : null);
                setLatestItems(parsedResponse?.context ? parsedResponse.context.data_points : []);
            } else {
                const result = (await chatClient.getCompletion(allMessages, options)) as ChatCompletionResponse;
                setAnswers([...answers, [question, result]]);
                setSessionState(result?.sessionState ? result.sessionState : null);
                setLatestItems(result?.context ? result.context.data_points : []);
            }
        } catch (e) {
            setError(e);
        } finally {
            setIsLoading(false);
        }
    };

    const checkThenMakeApiRequest = async (question: string) => {
        lastQuestionRef.current = question;
        if (question.match(/buy/)) {
            setIsBuy(true);
            return;
        }

        makeApiRequest(question);
    };

    const clearChat = () => {
        lastQuestionRef.current = "";
        if (error) {
            setError(undefined);
        }
        setActiveAnalysisPanelTab(undefined);
        setAnswers([]);
        setStreamedAnswers([]);
        setIsLoading(false);
        setIsStreaming(false);
    };

    useEffect(() => {
        chatMessageStreamEnd.current?.scrollIntoView({ behavior: "smooth" });
    }, [isLoading]);
    useEffect(() => {
        chatMessageStreamEnd.current?.scrollIntoView({ behavior: "auto" });
    }, [streamedAnswers]);

    const onTemperatureChange = (_ev: React.ChangeEvent<HTMLInputElement>, data: InputOnChangeData) => {
        setTemperature(parseFloat(data.value || "0"));
    };

    const onScoreThresholdChange = (_ev: React.ChangeEvent<HTMLInputElement>, data: InputOnChangeData) => {
        setScoreThreshold(parseFloat(data.value || "0"));
    };

    const onRetrieveCountChange = (_ev: React.ChangeEvent<HTMLInputElement>, data: InputOnChangeData) => {
        setRetrieveCount(parseInt(data.value || "3"));
    };

    const onShouldStreamChange = (_ev: React.ChangeEvent<HTMLInputElement>, data: CheckboxOnChangeData) => {
        setShouldStream(!!data.checked);
    };

    const onExampleClicked = (example: string) => {
        checkThenMakeApiRequest(example);
    };

    const onToggleTab = (tab: AnalysisPanelTabs, index: number) => {
        if (activeAnalysisPanelTab === tab && selectedAnswer === index) {
            setActiveAnalysisPanelTab(undefined);
        } else {
            setActiveAnalysisPanelTab(tab);
        }

        setSelectedAnswer(index);
    };

    // IDs for form labels and their associated callouts
    const temperatureId = useId();
    const temperatureFieldId = useId();
    const searchScoreId = useId();
    const searchScoreFieldId = useId();
    const retrieveCountId = useId();
    const retrieveCountFieldId = useId();
    const shouldStreamId = useId();
    const shouldStreamFieldId = useId();

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
                            <img
                                src={documentDB}
                                alt="Azure DocumentDB logo"
                                aria-label="Azure DocumentDB logo"
                                width="100px"
                                height="132px"
                                className={styles.emptyStateLogo}
                            />
                            <h1 className={styles.chatEmptyStateTitle}>FlavorGenius: Chat, Input, Discover</h1>
                            <h2 className={styles.chatEmptyStateSubtitle}>Ask anything or try an example</h2>
                            <ExampleList onExampleClicked={onExampleClicked} />
                        </div>
                    ) : (
                        <div className={styles.chatMessageStream}>
                            {isStreaming &&
                                streamedAnswers.map((streamedAnswer, index) => (
                                    <div key={index}>
                                        <UserChatMessage message={streamedAnswer[0]} />
                                        <div className={styles.chatMessageGpt}>
                                            <Answer
                                                isStreaming={true}
                                                key={index}
                                                answer={streamedAnswer[1]}
                                                isSelected={false}
                                                onThoughtProcessClicked={() => onToggleTab(AnalysisPanelTabs.ThoughtProcessTab, index)}
                                                onSupportingContentClicked={() => onToggleTab(AnalysisPanelTabs.SupportingContentTab, index)}
                                            />
                                        </div>
                                    </div>
                                ))}
                            {!isStreaming &&
                                answers.map((answer, index) => (
                                    <div key={index}>
                                        <UserChatMessage message={answer[0]} />
                                        <div className={styles.chatMessageGpt}>
                                            <Answer
                                                isStreaming={false}
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
                                        <AnswerError error={error.toString()} onRetry={() => checkThenMakeApiRequest(lastQuestionRef.current)} />
                                    </div>
                                </>
                            ) : null}
                            <div ref={chatMessageStreamEnd} />
                        </div>
                    )}

                    <div className={styles.chatInput}>
                        <QuestionInput
                            clearOnSend
                            placeholder="Type a new question (e.g. Are there any high protein dishes available?)"
                            disabled={isLoading}
                            onSend={question => checkThenMakeApiRequest(question)}
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

                <OverlayDrawer position="end" open={isCartOpen} onOpenChange={(_ev, data) => setIsCartOpen(data.open)}>
                    <DrawerHeader>
                        <DrawerHeaderTitle
                            action={<Button appearance="subtle" aria-label="Close" icon={<Dismiss24Regular />} onClick={() => setIsCartOpen(false)} />}
                        >
                            Cart Items
                        </DrawerHeaderTitle>
                    </DrawerHeader>
                    <DrawerBody>
                        <div>
                            {cartItems.map((item, index) => (
                                <h4 key={index}>- {item}</h4>
                            ))}
                        </div>
                    </DrawerBody>
                    <DrawerFooter>
                        <Button onClick={() => setIsCartOpen(false)}>Close</Button>
                    </DrawerFooter>
                </OverlayDrawer>
                <OverlayDrawer position="end" open={isConfigPanelOpen} onOpenChange={(_ev, data) => setIsConfigPanelOpen(data.open)}>
                    <DrawerHeader>
                        <DrawerHeaderTitle
                            action={<Button appearance="subtle" aria-label="Close" icon={<Dismiss24Regular />} onClick={() => setIsConfigPanelOpen(false)} />}
                        >
                            Configure answer generation
                        </DrawerHeaderTitle>
                    </DrawerHeader>
                    <DrawerBody>
                        <div className={styles.chatSettingsSeparator}>
                            <HelpCallout labelId={temperatureId} fieldId={temperatureFieldId} helpText={toolTipText.temperature} label="Temperature" />
                            <Input
                                id={temperatureFieldId}
                                type="number"
                                min={0}
                                max={1}
                                step={0.1}
                                defaultValue={temperature.toString()}
                                onChange={onTemperatureChange}
                                aria-labelledby={temperatureId}
                            />
                        </div>

                        <div className={styles.chatSettingsSeparator}>
                            <HelpCallout
                                labelId={searchScoreId}
                                fieldId={searchScoreFieldId}
                                helpText={toolTipText.searchScore}
                                label="Similarity Score Threshold"
                            />
                            <Input
                                id={searchScoreFieldId}
                                type="number"
                                min={0}
                                max={1}
                                step={0.1}
                                defaultValue={scoreThreshold.toString()}
                                onChange={onScoreThresholdChange}
                                aria-labelledby={searchScoreId}
                            />
                        </div>

                        <div className={styles.chatSettingsSeparator}>
                            <HelpCallout
                                labelId={retrieveCountId}
                                fieldId={retrieveCountFieldId}
                                helpText={toolTipText.retrieveNumber}
                                label="Retrieve this many search results:"
                            />
                            <Input
                                id={retrieveCountFieldId}
                                type="number"
                                min={1}
                                max={20}
                                defaultValue={retrieveCount.toString()}
                                onChange={onRetrieveCountChange}
                                aria-labelledby={retrieveCountId}
                            />
                        </div>

                        <VectorSettings
                            defaultRetrievalMode={retrievalMode}
                            updateRetrievalMode={(retrievalMode: RetrievalMode) => setRetrievalMode(retrievalMode)}
                        />

                        <div className={styles.chatSettingsSeparator}>
                            <HelpCallout
                                labelId={shouldStreamId}
                                fieldId={shouldStreamFieldId}
                                helpText={toolTipText.streamChat}
                                label="Stream chat completion responses"
                            />
                            <Checkbox id={shouldStreamFieldId} checked={shouldStream} onChange={onShouldStreamChange} aria-labelledby={shouldStreamId} />
                        </div>
                    </DrawerBody>
                </OverlayDrawer>
            </div>
        </div>
    );
};

export default Chat;
