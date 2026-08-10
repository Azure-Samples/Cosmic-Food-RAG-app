import React from "react";
import ReactDOM from "react-dom/client";
import { createHashRouter, RouterProvider } from "react-router-dom";
import { FluentProvider, webLightTheme } from "@fluentui/react-components";

import "./index.css";

import Layout from "./pages/layout/Layout";
import Chat from "./pages/chat/Chat";

const router = createHashRouter([
    {
        path: "/",
        element: <Layout />,
        children: [
            {
                index: true,
                element: <Chat />
            },
            {
                path: "*",
                lazy: () => import("./pages/NoPage")
            }
        ]
    }
]);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
    <React.StrictMode>
        <FluentProvider theme={webLightTheme} style={{ height: "100%", backgroundColor: "transparent" }}>
            <RouterProvider router={router} />
        </FluentProvider>
    </React.StrictMode>
);
