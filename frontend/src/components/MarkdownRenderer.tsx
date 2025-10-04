'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = '' }) => {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeRaw]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            
            if (!inline && language) {
              return (
                <SyntaxHighlighter
                  style={oneDark}
                  language={language}
                  PreTag="div"
                  className="rounded-lg border border-gray-700"
                  customStyle={{
                    margin: '1rem 0',
                    fontSize: '0.875rem',
                    lineHeight: '1.5',
                  }}
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              );
            }
            
            return (
              <code 
                className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm font-mono text-gray-800 dark:text-gray-200"
                {...props}
              >
                {children}
              </code>
            );
          },
          pre({ children, ...props }) {
            return (
              <pre 
                className="bg-gray-900 rounded-lg p-4 overflow-x-auto border border-gray-700"
                {...props}
              >
                {children}
              </pre>
            );
          },
          h1({ children, ...props }) {
            return (
              <h1 
                className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-6 mb-4 border-b border-gray-200 dark:border-gray-700 pb-2"
                {...props}
              >
                {children}
              </h1>
            );
          },
          h2({ children, ...props }) {
            return (
              <h2 
                className="text-xl font-semibold text-gray-900 dark:text-gray-100 mt-5 mb-3 border-b border-gray-200 dark:border-gray-700 pb-1"
                {...props}
              >
                {children}
              </h2>
            );
          },
          h3({ children, ...props }) {
            return (
              <h3 
                className="text-lg font-semibold text-gray-900 dark:text-gray-100 mt-4 mb-2"
                {...props}
              >
                {children}
              </h3>
            );
          },
          h4({ children, ...props }) {
            return (
              <h4 
                className="text-base font-semibold text-gray-900 dark:text-gray-100 mt-3 mb-2"
                {...props}
              >
                {children}
              </h4>
            );
          },
          h5({ children, ...props }) {
            return (
              <h5 
                className="text-sm font-semibold text-gray-900 dark:text-gray-100 mt-3 mb-2"
                {...props}
              >
                {children}
              </h5>
            );
          },
          h6({ children, ...props }) {
            return (
              <h6 
                className="text-xs font-semibold text-gray-900 dark:text-gray-100 mt-3 mb-2"
                {...props}
              >
                {children}
              </h6>
            );
          },
          p({ children, ...props }) {
            return (
              <p 
                className="text-gray-700 dark:text-gray-300 mb-3 leading-relaxed"
                {...props}
              >
                {children}
              </p>
            );
          },
          ul({ children, ...props }) {
            return (
              <ul 
                className="list-disc list-inside text-gray-700 dark:text-gray-300 mb-3 space-y-1"
                {...props}
              >
                {children}
              </ul>
            );
          },
          ol({ children, ...props }) {
            return (
              <ol 
                className="list-decimal list-inside text-gray-700 dark:text-gray-300 mb-3 space-y-1"
                {...props}
              >
                {children}
              </ol>
            );
          },
          li({ children, ...props }) {
            return (
              <li 
                className="text-gray-700 dark:text-gray-300"
                {...props}
              >
                {children}
              </li>
            );
          },
          blockquote({ children, ...props }) {
            return (
              <blockquote 
                className="border-l-4 border-blue-500 pl-4 py-2 my-4 bg-blue-50 dark:bg-blue-900/20 text-gray-700 dark:text-gray-300 italic"
                {...props}
              >
                {children}
              </blockquote>
            );
          },
          table({ children, ...props }) {
            return (
              <div className="overflow-x-auto my-4">
                <table 
                  className="min-w-full border-collapse border border-gray-300 dark:border-gray-600"
                  {...props}
                >
                  {children}
                </table>
              </div>
            );
          },
          thead({ children, ...props }) {
            return (
              <thead 
                className="bg-gray-50 dark:bg-gray-800"
                {...props}
              >
                {children}
              </thead>
            );
          },
          tbody({ children, ...props }) {
            return (
              <tbody 
                className="bg-white dark:bg-gray-900"
                {...props}
              >
                {children}
              </tbody>
            );
          },
          tr({ children, ...props }) {
            return (
              <tr 
                className="border-b border-gray-200 dark:border-gray-700"
                {...props}
              >
                {children}
              </tr>
            );
          },
          th({ children, ...props }) {
            return (
              <th 
                className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-gray-100"
                {...props}
              >
                {children}
              </th>
            );
          },
          td({ children, ...props }) {
            return (
              <td 
                className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-700 dark:text-gray-300"
                {...props}
              >
                {children}
              </td>
            );
          },
          a({ children, href, ...props }) {
            return (
              <a 
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline"
                {...props}
              >
                {children}
              </a>
            );
          },
          img({ src, alt, ...props }) {
            return (
              <img 
                src={src}
                alt={alt}
                className="max-w-full h-auto rounded-lg border border-gray-200 dark:border-gray-700 my-4"
                {...props}
              />
            );
          },
          hr({ ...props }) {
            return (
              <hr 
                className="my-6 border-gray-300 dark:border-gray-600"
                {...props}
              />
            );
          },
          strong({ children, ...props }) {
            return (
              <strong 
                className="font-semibold text-gray-900 dark:text-gray-100"
                {...props}
              >
                {children}
              </strong>
            );
          },
          em({ children, ...props }) {
            return (
              <em 
                className="italic text-gray-700 dark:text-gray-300"
                {...props}
              >
                {children}
              </em>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
