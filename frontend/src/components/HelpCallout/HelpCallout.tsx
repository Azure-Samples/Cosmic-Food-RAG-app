import { type JSX, useId, useState } from "react";
import { Button, Popover, PopoverTrigger, PopoverSurface } from "@fluentui/react-components";
import { Info24Regular } from "@fluentui/react-icons";

interface IHelpCalloutProps {
    label: string | undefined;
    labelId: string;
    fieldId: string | undefined;
    helpText: string;
}

export const HelpCallout = (props: IHelpCalloutProps): JSX.Element => {
    const [isCalloutVisible, setIsCalloutVisible] = useState(false);
    const descriptionId = useId();

    return (
        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <label id={props.labelId} htmlFor={props.fieldId}>
                {props.label}
            </label>
            <Popover open={isCalloutVisible} onOpenChange={(_ev, data) => setIsCalloutVisible(data.open)} trapFocus>
                <PopoverTrigger disableButtonEnhancement>
                    <Button appearance="transparent" icon={<Info24Regular />} title="Info" aria-label="Info" style={{ marginBottom: -3, flexShrink: 0 }} />
                </PopoverTrigger>
                <PopoverSurface aria-describedby={descriptionId} role="alertdialog" style={{ padding: 20, maxWidth: 300 }}>
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: "4px" }}>
                        <span id={descriptionId}>{props.helpText}</span>
                        <Button onClick={() => setIsCalloutVisible(false)}>Close</Button>
                    </div>
                </PopoverSurface>
            </Popover>
        </div>
    );
};
