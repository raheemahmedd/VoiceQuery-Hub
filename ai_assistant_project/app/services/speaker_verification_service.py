
import nemo.collections.asr as nemo_asr
import os
import torch
import torchaudio
import torch
from .speech_service import SpeechService
from ..db.users import  get_all_embeddings,get_user_name
from ..services.speech_service import SpeechService
class SpeakerVerfication:
    def __init__(self,speech_service: SpeechService):
        self.speaker_model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained("nvidia/speakerverification_en_titanet_large")
        ## pass the same object used for speech serivce to keep the audio path
        self.SpeechService_obj=speech_service
        self.fixed_path=""
        self.speaker_name=''
        self.speaker_role=''
        self.confidence_score=0

        
    def audio_resample(self): 
        info = torchaudio.info(self.SpeechService_obj.audio_path)
        print(f"Sample rate: {info.sample_rate}, Channels: {info.num_channels}, Duration: {info.num_frames / info.sample_rate:.2f}s")

        # Load and fix if necessary (resample to 16kHz, convert to mono)
        waveform, sample_rate = torchaudio.load(self.SpeechService_obj.audio_path)

        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # Resample to 16kHz
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resampler(waveform)
            print("the audio file is resampling!")
            fixed_audio_dir=r"E:\projects-in-army\1\Voice-Enabled Agentic Predictive Maintenance with Biometric Alerts\ai_assistant_project\uploads\fixed_audioes"
            # Save the fixed mono 16kHz version to avoid repeated issues
            filename, _ = os.path.splitext(self.SpeechService_obj.audio_file_name)

            self.fixed_path = rf"{fixed_audio_dir}\{filename}_fixed.mp3"
           
            if waveform.dim() == 3:
                waveform = waveform.squeeze(-1)  # Remove extra dimension if present (e.g., [1, time, 1] -> [1, time])

            torchaudio.save(self.fixed_path, waveform, 16000)
            print(f"Fixed audio saved to: {self.fixed_path}")
            return
        
        self.fixed_path= self.SpeechService_obj.audio_path       



    def audio_embedding(self,fixed_path):
        # Extract embedding (use the fixed path if you created one)
        emb = self.speaker_model.get_embedding(fixed_path)  # Or use original if it's already mono 16kHz
        return emb
    

    
    def verfication_similarity(self):
        
        emb1=self.audio_embedding(self.fixed_path)
        
        # Normalize to unit vectors
        emb1 = torch.nn.functional.normalize(emb1, p=2, dim=1)
      
        
        ##############################################
            ### select embeddings from db ###
        ###############################################
        db_embds=get_all_embeddings()
        for embedding, user_id in db_embds:
                
                emb2=torch.tensor(embedding)
                
                emb2 = torch.nn.functional.normalize(emb2, p=2, dim=1)
                
                cos_sim = torch.nn.functional.cosine_similarity(emb1, emb2)
                
                
                are_same = torch.equal(emb1, emb2)
                if are_same:
                    print("both embds are the same")
                    
                self.confidence_score=cos_sim.item()
                
                print("Cosine similarity:", int((cos_sim.item())*100),"%")
                if cos_sim.item() > 0.50:
                  ### get the name of the speaker from db then break ###
        
                     user_data=get_user_name(user_id)
                     for user_name,user_role in user_data:
                        self.speaker_name=user_name
                        self.speaker_role=user_role
                     print("The speaker voice verfied well 💪")
                     print(f"The speaker name is {user_name} working as {user_role}")
                     return True , user_id
        
        return False , ''
    
                
if __name__ == "__main__":
   

    s=SpeechService("demoz")
    print("before transcripe",s.audio_path)
    transcript = s.transcribe(r"ai_assistant_project\tests\samples\sample_voice_1.wav")
    print("after transcripe",s.audio_path)
    print("Transcript:", transcript)

    sv=SpeakerVerfication(s)
    sv.audio_resample()
    sv.verfication_similarity()

