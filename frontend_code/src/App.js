import './App.scss';
import FileBase64 from 'react-file-base64';
import {useEffect, useRef, useState} from "react";
import axios from "axios";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import micLogo from './microphone-solid.svg';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
    // let imagesTemp = ['IMG_7982.jpg', 'IMG_7982.jpg', 'IMG_7982.jpg', 'IMG_7982.jpg', 'IMG_7982.jpg', 'IMG_7982.jpg'];
    const [images, setImages] = useState([]);
    const [searchDisabled, setSearchDisabled] = useState(false);
    const [micLogoClass, setMicLogoClass] = useState('');

    const inputRef = useRef()
    const customLabelsRef = useRef()

    const {
        transcript,
        listening,
        resetTranscript,
        browserSupportsSpeechRecognition
    } = useSpeechRecognition();

    useEffect(() => {
        inputRef.current.value = transcript;
    }, [transcript])

    useEffect(() => {
        if (listening) {
            setMicLogoClass('active')
        } else {
            setMicLogoClass('')
        }
    }, [listening])

    if (!browserSupportsSpeechRecognition) {
        return <span>Browser doesn't support speech recognition.</span>;
    }

    const search = () => {
        setSearchDisabled(true);
        let q = inputRef.current.value;
        console.log(q);
        console.log(q);
        (async () => {
            try {
                const config = {
                    headers: {
                        'x-api-key': 'lol-gif-aby-ccbd-a2lol-gif-aby-ccbd-a2lol-gif-aby-ccbd-a2lol-gif-aby-ccbd-a2'
                    }
                };
                const result = await axios.get('https://bhrg9dwg9d.execute-api.us-east-1.amazonaws.com/prod/search?q='
                    + encodeURIComponent(q), config);
                console.log(result.data);
                if (result.data['images']) {
                    setImages(result.data.images);
                } else {
                    setImages([])
                }

                setSearchDisabled(false);
            } catch (e) {
                toast("Failed to search. Try again!")
                setSearchDisabled(false);
            }

        })();
    }

    const uploadToS3 = (req) => {
        if (!req || req.length === 0)
            return

        let file = req[0].file
        const config = {
            headers: {
                'Content-Type': file.type,
                'x-amz-meta-customLabels': customLabelsRef.current.value
            },
            onUploadProgress: (progressEvent) => {
                const { loaded, total } = progressEvent;
                const percentCompleted = Math.round((loaded * 100) / total);
                console.log(`${percentCompleted}% uploaded`);
            }
        };

        const url = 'https://bhrg9dwg9d.execute-api.us-east-1.amazonaws.com/prod/upload/ccbd-b2-photos-ga/' + file.name;

        return axios.put(url, file, config)
            .then((response) => {
                console.log('File uploaded successfully!', response);
                toast("File upload successful!")
            })
            .catch((error) => {
                console.error('Error uploading file!', error);
                toast("File upload failed!")
            });
    };

    const startListening = () => {
        if (listening) {
            SpeechRecognition.stopListening();
        } else {
            SpeechRecognition.startListening();
        }
    }
    return (
        <div className={'App'}>
            <h1 style={{color: "gray", marginLeft: '24px'}}>Photo Album</h1>
            <div className={'search-box'}>
                <input className={'search'} ref={inputRef} placeholder={'Search images'} type={'text'}/>
                <img onClick={startListening} className={`mic-logo ${micLogoClass}`} src={micLogo}/>
                <button disabled={searchDisabled} onClick={search}>Search</button>
                <div className={'upload-box'}>
                    <input type={'text'} ref={customLabelsRef} className={'custom-labels'} placeholder={'Add custom labels here'}/>
                    <FileBase64
                        multiple={true}
                        onDone={(x) => uploadToS3(x)}/>
                </div>
            </div>
            <div className={'album'}>
                {images.map(img => <img alt={'img'} src={'https://ccbd-b2-photos-ga.s3.amazonaws.com/' + img} />)}
                {/*{images.map(img => <img alt={'img'}*/}
                {/*                        src={'https://www.stockvault.net/data/2011/01/20/117250/preview16.jpg'}/>)}*/}
            </div>
            <ToastContainer />
        </div>

    );
}

export default App;
