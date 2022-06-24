const {
    TranscribeStreamingClient,
    StartStreamTranscriptionCommand
} = require("@aws-sdk/client-transcribe-streaming");
const { RtmTokenBuilder, RtmRole } = require('agora-access-token')
const AWS = require("aws-sdk");
const { v4: uuidv4 } = require('uuid');

const {
    AWS_REGION,
    TRANSCRIBE_LANGUAGE_CODE,
    // VOCABULARY_FILTER,
    MEDIA_SAMPLE_RATE_HERTZ,
    // VOCABULARY_NAME,
    // AWS_GW_WS,
    TRANSLATE_ENABLED,
    // TRANSLATE_WEB_SOCKET_URL,
    // VOCABULARY_FILTER_METHOD,
    MEDIA_ENCODING,
    // WRITER_WEBSOCKET_SENDTRANSCRIPTION_ROUTE,
    SOURCE_TRANSLATE_LANGUAGE_CODE,
    TARGET_TRANSLATE_LANGUAGE_CODES,
    ALL_LANGUAGE_CODES,
    ALL_TRUE_LANGUAGE_CODES,
    // DEFAULT_LANGUAGE_CODE,
    SUCCESS_EXIT_CODE,
    ERROR_EXIT_CODE,
    TWO_ROW_CHARACTER_COUNT,
    RTM_CHANNEL,
    AGORA_APP_ID,
    AGORA_APP_CERT
} = require("./constants");

const ALL_LANGUAGE_CODES_LIST = ALL_LANGUAGE_CODES.split(":")
const ALL_TRUE_LANGUAGE_CODES_LIST = ALL_TRUE_LANGUAGE_CODES.split(":")

const GOOGLE_TRANSCRIBE_LANGUAGE_CODE = TRANSCRIBE_LANGUAGE_CODE == "zh-CN" ? "zh" : TRANSCRIBE_LANGUAGE_CODE;

let START_TIMESTAMP = Date.now();

const RTM_USER_ID = "system-live-caption"
let RTM_TOKEN = RtmTokenBuilder.buildToken(AGORA_APP_ID, AGORA_APP_CERT, RTM_USER_ID, RtmRole, Math.floor(Date.now() / 1000) + 3600 * 24);
let RTM_TOKEN_TIMESTAMP = Date.now()

const translateClient = new AWS.Translate({
    apiVersion: "2018-11-29",
    region: AWS_REGION,
});

const https = require('https')

const sendRtmMessage = (msg) => {
    msg.languageCode = ALL_LANGUAGE_CODES_LIST[ALL_TRUE_LANGUAGE_CODES_LIST.indexOf(msg.languageCode)]
    // RTM Token
    // 生成 RTM Token 时使用的 user ID
    const rtm_msg = {
        "type": "EVENT",
        "id": uuidv4(),
        "from": {
            "id": "system",
            "avatar": "system",
            "nickname": "system"
        },
        "content": {
            "type": "SUBTITLE",
            "subtitleInfo": msg
        }
    }    
    console.log(rtm_msg)
    const data = JSON.stringify({
        channel_name: RTM_CHANNEL,
        payload: JSON.stringify(rtm_msg)
    })
    // 设置请求参数
    const options = {
        hostname: 'api.agora.io',
        port: 443,
        path: '/dev/v2/project/' + AGORA_APP_ID + '/rtm/users/' + RTM_USER_ID + '/channel_messages',
        method: 'POST',
        headers: {
            // 在 header 中添加 x-agora-token 字段
            'x-agora-token': RTM_TOKEN,
            // 在 header 中添加 x-agora-uid 字段
            'x-agora-uid': RTM_USER_ID,
            'Content-Type': 'application/json'
        }
    }

    const req = https.request(options, res => {
        console.log(`Status code: ${res.statusCode}`)
        res.on('data', d => {
            process.stdout.write(d)
        })
    })

    req.on('error', error => {
        console.error(error)
    })

    req.write(data)
    req.end()
}

const TRANSLATELanguageCodes = TARGET_TRANSLATE_LANGUAGE_CODES.split(":");
console.log("Languages to translate to: ", TRANSLATELanguageCodes);

// const metadataManager = require("./metadataManager");
// const WebSocketManager = require("./utils/webSocketManager");
const shortenText = require("./shortenText");
// const { OVERLAYS_UTILS } = require("./utils");

// const directTranscriptionWSManager = new WebSocketManager(AWS_GW_WS);
// directTranscriptionWSManager.connect();

// let translateTranscriptionWSManager;
// if (TRANSLATE_ENABLED == 'true') {
//     translateTranscriptionWSManager = new WebSocketManager(TRANSLATE_WEB_SOCKET_URL);
//     translateTranscriptionWSManager.connect();
// }

// let overlaysInformation = null;
let endTimePrev = null;
let feedTime = process.argv[2];
let previousSentCaptionEndTime = 0;

const processTranslation = async (transcriptData, targetLanguageCode) => {
    try {
        const translateRequest = translateClient.translateText({
            SourceLanguageCode: SOURCE_TRANSLATE_LANGUAGE_CODE,
            TargetLanguageCode: targetLanguageCode,
            Text: transcriptData.text,
        });
        const translateResult = await translateRequest.promise();

        const data = {
            text: shortenText(translateResult.TranslatedText, targetLanguageCode),
            // text: translateResult.TranslatedText,
            startTime: transcriptData.startTime,
            endTime: transcriptData.endTime,
            streamSendTime: transcriptData.streamSendTime,
            transcribeFinishTime: transcriptData.transcribeFinishTime,
            translateFinishTime: Date.now(),
            partial: transcriptData.partial,
            languageCode: targetLanguageCode
        };

        sendRtmMessage(data)
        //   if (data) {
        //     const parsedTranscriptionWithCaptionsFormatted = formatCaptions(data, targetLanguageCode);
        //   }
        //   if (sendTranslationWebSocketManager.connected) {
        //     const payload = {
        //       action: WRITER_WEBSOCKET_SENDTRANSCRIPTION_ROUTE,
        //       data: data,
        //       lang: targetLanguageCode,
        //     };
        //     sendTranslationWebSocketManager.send(payload);
        //   }

    } catch (error) {
        console.error(error.message);
    }
};

const processCaption = async function (parsedTranscription) {
    if (Date.now() - RTM_TOKEN_TIMESTAMP > 1000 * 3600 * 23) {
        RTM_TOKEN = RtmTokenBuilder.buildToken(AGORA_APP_ID, AGORA_APP_CERT, RTM_USER_ID, RtmRole, Math.floor(Date.now() / 1000) + 3600 * 24);
        RTM_TOKEN_TIMESTAMP = Date.now();
    }

    // once per second
    if (parsedTranscription && (Date.now() - START_TIMESTAMP > 3000 || parsedTranscription.partial === false)) {
        START_TIMESTAMP = Date.now();

        // only format captions for transcriptions that are sent directly to the writer websocket,
        // captions for transcriptions that are going to be translated will be formatted later
        const parsedTranscriptionWithCaptionsFormatted = formatCaptions(parsedTranscription, TRANSCRIBE_LANGUAGE_CODE);

        sendRtmMessage(parsedTranscriptionWithCaptionsFormatted)



        if (TRANSLATE_ENABLED == 'true') {
            // if (parsedTranscription.partial === false) {

            const caption = buildCaption(parsedTranscription);
            if (caption) {
                await Promise.allSettled(TRANSLATELanguageCodes.map((translationLanguageCode) => processTranslation(caption, translationLanguageCode)));
            }
            // }
        }
    }
}

async function googleTranscribe() {
    // [START speech_transcribe_infinite_streaming]

    const encoding = 'LINEAR16';
    const sampleRateHertz = MEDIA_SAMPLE_RATE_HERTZ;
    const languageCode = GOOGLE_TRANSCRIBE_LANGUAGE_CODE;
    // const streamingLimit = 50000;
    const streamingLimit = 120000; // ms - 最大只能取到五分钟的一半

    const { Writable } = require('stream');

    // Imports the Google Cloud client library
    // Currently, only v1p1beta1 contains result-end-time
    const speech = require('@google-cloud/speech').v1p1beta1;

    const client = new speech.SpeechClient();

    const config = {
        encoding: encoding,
        sampleRateHertz: sampleRateHertz,
        languageCode: languageCode,
    };

    const request = {
        config,
        interimResults: true,
    };

    let recognizeStream = null;
    let restartCounter = 0;
    let audioInput = [];
    let lastAudioInput = [];
    let resultEndTime = 0;
    let isFinalEndTime = 0;
    let finalRequestEndTime = 0;
    let newStream = true;
    let bridgingOffset = 0;
    let lastTranscriptWasFinal = false;

    function startStream() {
        // Clear current audioInput
        audioInput = [];
        // Initiate (Reinitiate) a recognize stream
        recognizeStream = client
            .streamingRecognize(request)
            .on('error', err => {
                if (err.code === 11) {
                    // restartStream();
                } else {
                    console.error('API request error ' + err);
                }
            })
            .on('data', speechCallback);
        // Restart stream when streamingLimit expires
        setTimeout(restartStream, streamingLimit);
    }

    const speechCallback = async (stream) => {
        // Convert API result end time from seconds + nanoseconds to milliseconds
        resultEndTime =
            stream.results[0].resultEndTime.seconds * 1000 +
            Math.round(stream.results[0].resultEndTime.nanos / 1000000);

        // Calculate correct time based on offset from audio sent twice
        // console.log((resultEndTime - bridgingOffset + streamingLimit * restartCounter) / 1000, feedTime)
        const correctedTime =
            parseFloat((resultEndTime - bridgingOffset + streamingLimit * restartCounter) / 1000) + parseFloat(feedTime);
        let googleCaption = {
            streamSendTime: "",
            transcribeFinishTime: Date.now(),
            text: stream.results[0].alternatives[0].transcript,
            startTime: correctedTime,
            endTime: correctedTime,
            partial: !stream.results[0].isFinal
        }
        await processCaption(googleCaption)
        if (stream.results[0].isFinal) {
            isFinalEndTime = resultEndTime;
            lastTranscriptWasFinal = true;
        } else {
            lastTranscriptWasFinal = false;
        }
    };

    const audioInputStreamTransform = new Writable({
        write(chunk, encoding, next) {
            if (newStream && lastAudioInput.length !== 0) {
                // Approximate math to calculate time of chunks
                const chunkTime = streamingLimit / lastAudioInput.length;
                if (chunkTime !== 0) {
                    if (bridgingOffset < 0) {
                        bridgingOffset = 0;
                    }
                    if(resultEndTime !== 0){
                        if (bridgingOffset > finalRequestEndTime) {
                            bridgingOffset = finalRequestEndTime;
                        }
                        const chunksFromMS = Math.floor(
                            (finalRequestEndTime - bridgingOffset) / chunkTime
                        );
                        bridgingOffset = Math.floor(
                            (lastAudioInput.length - chunksFromMS) * chunkTime
                        );

                        for (let i = chunksFromMS; i < lastAudioInput.length; i++) {
                            if (recognizeStream) {
                                recognizeStream.write(lastAudioInput[i]);
                            }
                        }
                    }else{
                        bridgingOffset = 0;
                    }
                }
                newStream = false;
            }

            audioInput.push(chunk);

            if (recognizeStream) {
                recognizeStream.write(chunk);
            }

            next();
        },

        final() {
            if (recognizeStream) {
                recognizeStream.end();
            }
        },
    });
    // audioInputStreamTransform._writableState.highWaterMark = 4096;

    function restartStream() {
        if (recognizeStream) {
            recognizeStream.end();
            recognizeStream.removeListener('data', speechCallback);
            recognizeStream = null;
        }
        if (resultEndTime > 0) {
            finalRequestEndTime = isFinalEndTime;
        }
        resultEndTime = 0;

        lastAudioInput = [];
        lastAudioInput = audioInput;

        restartCounter++;

        if (!lastTranscriptWasFinal) {
            process.stdout.write('\n');
        }
        process.stdout.write(
            `${streamingLimit * restartCounter}: RESTARTING REQUEST\n`
        );

        newStream = true;

        startStream();
    }
    // Start recording and send the microphone input to the Speech API
    process.stdin.on("close", () => {
        console.log("readable stream close");
        process.exit(200604);
    })
    process.stdin.on("end", () => {
        console.log("readable stream end");
        process.exit(200604);
    })
    process.stdin.resume();
    process.stdin.pipe(audioInputStreamTransform);

    console.log('');
    console.log('Listening, press Ctrl+C to stop.');
    console.log('');
    console.log('End (ms)       Transcript Results/Status');
    console.log('=========================================================');

    startStream();
    // [END speech_transcribe_infinite_streaming]
}

const awsTranscribe = async function () {
    process.stdin._writableState.highWaterMark = 4096; // Read with chunk size of 3200 as the audio is 16kHz linear PCM
    process.stdin.resume();
    const transcribeInput = async function* () {
        for await (const chunk of process.stdin) {
            if (chunk.length > 6000) continue;
            yield { AudioEvent: { AudioChunk: chunk } };
        }
    };

    const transcribeClient = new TranscribeStreamingClient({
        region: AWS_REGION,
    });

    const startStreamTranscriptionCommand = new StartStreamTranscriptionCommand({
        LanguageCode: TRANSCRIBE_LANGUAGE_CODE,
        // VocabularyName: VOCABULARY_NAME,
        // VocabularyFilterName: VOCABULARY_FILTER,
        // VocabularyFilterMethod: VOCABULARY_FILTER_METHOD,
        MediaSampleRateHertz: MEDIA_SAMPLE_RATE_HERTZ,
        MediaEncoding: MEDIA_ENCODING,
        AudioStream: transcribeInput(),
    });

    const startStreamTranscriptionCommandOutput = await transcribeClient.send(
        startStreamTranscriptionCommand
    );

    console.log(
        `AWS Transcribe connection status code: ${startStreamTranscriptionCommandOutput.$metadata.httpStatusCode}`
    );

    for await (const transcriptionEvent of startStreamTranscriptionCommandOutput.TranscriptResultStream) {

        const streamSendTime = Date.now();

        if (transcriptionEvent.TranscriptEvent.Transcript) {
            const results = transcriptionEvent.TranscriptEvent.Transcript.Results;
            // metadataManager.sendOverlaysMetadata(results, overlaysInformation);

            const parsedTranscription = parseTranscription(results, streamSendTime);

            await processCaption(parsedTranscription)

        }
    }
};

const startStreamingWrapper = async function () {
    try {
        await awsTranscribe();       
        process.exit(SUCCESS_EXIT_CODE);
    } catch (error) {
        console.log("Streaming error: ", error);
        process.exit(ERROR_EXIT_CODE);
    }
};

// const getOverlays = async () => {
//     try {
//         let utilsResponse = await OVERLAYS_UTILS.getOverlaysMapAndPattern();
//         overlaysInformation = utilsResponse;
//     } catch (ex) {
//         console.log("Overlays couldn't be loaded. Exception throwed: ", ex);
//     }
// };

const parseTranscription = (results, streamSendTime) => {
    let startTime = null;
    let endTime = null;

    if (results && results.length > 0) {
        if (results[0].Alternatives.length > 0) {
            const transcriptText = results[0].Alternatives[0].Transcript;
            // const decodedTranscriptText = decodeURIComponent(escape(transcriptText));

            startTime = endTimePrev || (+feedTime + +results[0].StartTime);
            endTime = +feedTime + +results[0].EndTime;
            endTimePrev = endTime;

            if (results[0].IsPartial === false) {
                endTimePrev = null;
            }

            // console.info(
            //     new Date(),
            //     "[Transcription to send to WebSocket] Feed Time: ",
            //     feedTime,
            //     ", Transcribe Start time: ",
            //     results[0].StartTime,
            //     ", Transcribe End Time: ",
            //     results[0].EndTime,
            //     ", Final Start time: ",
            //     startTime,
            //     ", Final End Time: ",
            //     endTime,
            //     ", Result Id ",
            //     results[0].ResultId,
            //     ", Is Partial: ",
            //     results[0].IsPartial
            // );

            return {
                streamSendTime: streamSendTime,
                transcribeFinishTime: Date.now(),
                text: transcriptText,
                startTime,
                endTime,
                partial: results[0].IsPartial,
            };
        }

        return null;
    }

    return null;
};

const formatCaptions = (parsedTranscription, language_code) => {

    return {
        ...parsedTranscription,
        text: shortenText(parsedTranscription.text, language_code),
        languageCode: language_code
    }

};

const getDisplayTime = (text) => {
    if (text.length <= TWO_ROW_CHARACTER_COUNT) return 4;
    return text.length / 20;
};

const buildCaption = (total) => {
    const caption = {};
    caption.partial = total.partial;
    caption.text = total.text;
    caption.startTime = total.startTime > previousSentCaptionEndTime ? total.startTime : previousSentCaptionEndTime;
    caption.endTime = caption.startTime + getDisplayTime(total.text);
    caption.streamSendTime = total.streamSendTime;
    caption.transcribeFinishTime = total.transcribeFinishTime;

    previousSentCaptionEndTime = caption.endTime;

    return caption;
};

// console.log("google")
// googleTranscribe();
// getOverlays();
if(TRANSCRIBE_LANGUAGE_CODE == "uk-UA"){
    console.log("google")
    googleTranscribe();
}else{
    console.log("aws")
    startStreamingWrapper();
} 


