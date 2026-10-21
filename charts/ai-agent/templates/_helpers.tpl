{{- define "ai-agent.name" -}}
{{- required "agentName is required" .Values.agentName | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ai-agent.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ai-agent.name" . }}
{{- end -}}

{{- define "ai-agent.labels" -}}
{{ include "ai-agent.selectorLabels" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Values.image.tag | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}

{{- define "ai-agent.image" -}}
{{- $repo := required "image.repository is required" .Values.image.repository -}}
{{- $tag := required "image.tag is required" .Values.image.tag -}}
{{- printf "%s:%s" $repo $tag -}}
{{- end -}}
